import docker
import os
import asyncio

DEFAULT_VOLUMES = [f"{os.path.abspath('config/')}:/tmp/configuration"]
DEFAULT_IMAGE = "registry.redhat.io/3scale-amp2/apicast-gateway-rhel8:3scale2.11"
DEFAULT_PORTS = {'8080/tcp': 8080}

class Apicast:
    running_containers = {}

    def __init__(
        self,
        volumes=DEFAULT_VOLUMES,
        image=DEFAULT_IMAGE,
        ports=DEFAULT_PORTS,
        environments={},
        network_mode=None,
        dns=None
    ):
        self.volumes = volumes
        self.image = image
        self.ports = ports
        self.environments = environments
        self.network_mode = network_mode
        self.dns = dns

    @staticmethod
    def stop_containers(id):
        if id in Apicast.running_containers:
            Apicast.running_containers[id].stop()
            del Apicast.running_containers[id]

    async def start_container(self):
        client = docker.from_env()
        container = client.containers.run(
            self.image,
            detach=True,
            volumes=self.volumes,
            auto_remove=True,
            ports=self.ports,
            environment=self.environments,
            #network_mode=self.network_mode,
            dns=self.dns
        )
        container.reload()
        Apicast.running_containers[container.id] = container
        await self.print_logs(container)

    async def print_logs(self, container):
        logs_generator = container.logs(stream=True)
        import threading
        with open(f"logs/{container.name}.log", "w") as out:
            t = threading.Thread(
                target=await_logs, args=(logs_generator, out))
            t.start()

            # the generator is blocking so we need to make this async manually
            while True:
                if t.is_alive():
                    await asyncio.sleep(1)
                else:
                    break

def await_logs(generator, out):
    for line in generator:
        out.write(f"{line.strip().decode('utf-8')}\n")
        out.flush()
    return 0
