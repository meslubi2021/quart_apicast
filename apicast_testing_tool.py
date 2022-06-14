from quart import Quart
from quart import render_template
from quart import abort, redirect, url_for
from quart import request
from containers.apicast import Apicast
import asyncio
import os
import logging
import validators
import re

logger = logging.getLogger(__name__)
app = Quart(__name__)

CUSTOM_FILES_FOLDER = "cmz"
version = "0.0.1"
a_images = [
    {
        "name":"3scale2.10",
        "value":"registry.redhat.io/3scale-amp2/apicast-gateway-rhel8:3scale2.10"
    },
    {
        "name":"3scale2.11",
        "value":"registry.redhat.io/3scale-amp2/apicast-gateway-rhel8:3scale2.11"
    }
]

@app.route("/")
async def index():
    return await render_homepage()

@app.route("/data", methods=['POST'])
async def post_data():
    form = await request.form
    if 'button_submit' in form:
        apicast_configuration = {}

        # get main configuration
        apicast_configuration['a_image'] = form.get('a_image')
        apicast_configuration['mock_auth'] = form.get('mock_auth')
        config_from = form.get('portal_endpoint')
        backend_endpoint = form.get('backend_endpoint')

        # get other env vars
        env_vars = {}
        for n, v in fields_selector("env_name_", "env_value_", 0):
            if form.get(n) and form.get(v):
                env_vars[form.get(n)] = form.get(v)
            else:
                break
        
        # get ports
        ports = {}
        for n, v in fields_selector("port_c_", "port_h_", 0):
            if form.get(n) and form.get(v):
                ports[form.get(n)] = form.get(v)
            else:
                break

        # mount files
        mounts = []
        for n,v in fields_selector("file_content_", "file_mount_", 0):
            if form.get(n) and form.get(v):
                content = form.get(n)
                mount = form.get(v)
                create_custom_file_for_mount(content, mount)
                mounts.append(mount)
            else:
                break
            
        # translate main configuration into env vars
        if config_from and re.match("[a-zA-Z0-9\-_]+\.json", config_from):
            config_from = f"/tmp/configuration/{config_from}"
        elif not config_from or not validators.url(config_from):
            logger.warn("A valid portal endpoint or local configuration file path `config/<name>.json` is required.")
            return
        env_vars["APICAST_CONFIGURATION"] = config_from
        if backend_endpoint:
            env_vars["BACKEND_ENDPOINT_OVERRIDE"] =  backend_endpoint
        apicast_configuration['env_vars'] = env_vars
        apicast_configuration['ports'] = ports
        apicast_configuration['mounts'] = mounts

        await start_apicast(apicast_configuration)
    elif 'kill' in form:
        Apicast.stop_containers(form['id'])

    return redirect(url_for("index"))

async def render_homepage():
    return await render_template('index.html', version=version, a_images=a_images, running_containers=Apicast.running_containers)

def fields_selector(prefix1, prefix2, n):
    while True:
        yield prefix1 + str(n), prefix2 + str(n)
        n = n+1

async def start_apicast(apicast_configuration):
    #network_mode = "host"
    image = apicast_configuration.get('a_image')
    # add default env vars here, then merge with env_vars
    env_vars = {}
    env_vars["THREESCALE_CONFIG_FILE"] = "/tmp/configuration/config.json"
    env_vars["THREESCALE_DEPLOYMENT_ENV"] = "staging"
    env_vars["APICAST_LOG_LEVEL"] = "debug"

    env_vars = env_vars | apicast_configuration.get('env_vars')
    volumes = [f"{os.path.abspath('config/')}:/tmp/configuration"]
    dns = ["8.8.8.8", "8.8.4.4"]
    ports = {}
    
    for p in apicast_configuration.get('ports'):
        ports[f"{p}/tcp"] = apicast_configuration.get('ports')[p]
    
    if apicast_configuration.get('mock_auth'):
        env_vars['BACKEND_ENDPOINT_OVERRIDE'] = "http://127.0.0.1:8081"
    elif "BACKEND_ENDPOINT_OVERRIDE" not in env_vars:
        logger.warn("A valid backend URL is required when not using mock auth.")
        return
    for m in apicast_configuration['mounts']:
        name = name_from_path(m)
        volumes.append(f"{os.path.abspath(CUSTOM_FILES_FOLDER)}/{name}:{m}")

    a = Apicast(image=image, environments=env_vars, volumes=volumes, dns=dns, ports=ports)   
    
    loop = asyncio.get_event_loop()
    loop.create_task(a.start_container())
    await asyncio.sleep(0)

def name_from_path(path):
    return path.split("/")[-1]

def create_custom_file_for_mount(file_content, path):
    name = name_from_path(path)
    with open(f"{CUSTOM_FILES_FOLDER}/{name}", "w") as file:
        file.write(file_content)