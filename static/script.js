$(function () {
    $('#local_config').on('click', function () {
        if ($(this).is(':checked')) {
            $('#portal_endpoint').attr('disabled', true);
            $('#portal_endpoint').attr('value', 'config/config.json');
        } else {
            $('#portal_endpoint').attr('disabled', false);
            $('#portal_endpoint').attr('value', '');
        }
    });
});

$(function () {
    $('#mock_auth').on('click', function () {
        if ($(this).is(':checked')) {
            $('#backend_endpoint').attr('disabled', true);
            $('#backend_endpoint').attr('value', 'http://127.0.0.1:8081');
        } else {
            $('#backend_endpoint').attr('disabled', false);
            $('#backend_endpoint').attr('value', '');
        }
    });
});

function addEnvVarFields() {
    var new_env_no = parseInt($('#total_envs').val()) + 1;
    
    var new_input = "<input class='table-cell' type='text' id='env_name_" + new_env_no + "' name='env_name_" + new_env_no + "' placeholder='Name'></input>= <input class='table-cell' type='text' id='env_value_" + new_env_no + "' name='env_value_" + new_env_no + "' placeholder='Value'></input><br>";

    $('#environment-variables').append(new_input);

    $('#total_envs').val(new_env_no);
}

function addPortsFields() {
    var new_port_no = parseInt($('#total_ports').val()) + 1;
    
    var new_input = "<input class='table-cell' type='text' id='port_c_" + new_port_no + "' name='port_c_" + new_port_no + "' placeholder='Container port' value=8080></input>: <input class='table-cell' type='text' id='port_h_" + new_port_no + "' name='port_h_" + new_port_no + "' placeholder='Host port'></input><br>";

    $('#ports').append(new_input);

    $('#total_ports').val(new_port_no);
}

function addFileFields() {
    var new_file_no = parseInt($('#total_files').val()) + 1;
    
    var new_input = "<textarea rows='12' cols='50' class='table-cell' type='text' id='file_content_" + new_file_no + "' name='file_content_" + new_file_no + "' placeholder='Paste file content here'></textarea>-> <input class='table-cell' type='text' id='file_mount_" + new_file_no + "' name='file_mount_" + new_file_no + "' placeholder='Mount point'></input><br>";

    $('#file-mounts').append(new_input);

    $('#total_files').val(new_file_no);
}
