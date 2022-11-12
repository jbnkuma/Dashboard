/**
 * Created by Jesus Becerril Navarrete on 06/06/15.
 */

$(document).ready(function (e) {
    $("#add_server").on('click', function () {
        $("#capa").attr('src', '/add_server/');
    });

    $("#upload_servers").on('click', function () {
        $("#capa").attr('src', '/upload_servers/');
    });

    $("#modify_server").on('click', function () {
        $("#capa").attr('src', '/modify_server/');
    });

    $("#server_inventory").on('click', function () {
        $("#capa").attr('src', '/inventory/');
    });

    $("#prod_inventory").on('click', function () {
        $("#capa").attr('src', '/prod_inventory/');
    });

    $("#uat_inventory").on('click', function () {
        $("#capa").attr('src', '/uat_inventory/');
    });

    $("#stress_inventory").on('click', function () {
        $("#capa").attr('src', '/stress_inventory/');
    });

    $("#search").on('click', function () {
        $("#capa").attr('src', '/searching_server/');
    });

    $("#monn").on('click', function () {
        $("#capa").attr('src', '/monitoring/');
    });

    $("#get_report").on('click', function () {
        $("#capa").attr('src', '/get_report/');
    });

    $("#change_console").on('click', function () {
        $("#capa").attr('src', '/change_console/');
    });

    $("#changes_inventory").on('click', function () {
        $("#capa").attr('src', '/change_inventory/');
    });

    $("#incidents_console").on('click', function () {
        $("#capa").attr('src', '/incident/');
    });

    $("#incidents_inventory").on('click', function () {
        $("#capa").attr('src', '/incidents_inventory/');
    });

    $("#log_up").on('click', function () {
        $("#capa").attr('src', '/upload_log/');
    });

    $("#search_logs").on('click', function () {
        $("#capa").attr('src', '/search_storelog/');
    });

    $("#search_logs").on('click', function () {
        $("#capa").attr('src', '/search_storelog/');
    });

    $("#search_plogs").on('click', function () {
        $("#capa").attr('src', '/search_plog/');
    });

    $("#p_prod").on('click', function () {
        $("#capa").attr('src', '/process_environment/?proc_env=producción&proc_env2=produccion');
    });

    $("#p_uat").on('click', function () {
        $("#capa").attr('src', '/process_environment/?proc_env=uat&proc_env2=uat');
    });

    $("#p_stress").on('click', function () {
        $("#capa").attr('src', '/process_environment/?proc_env=stress&proc_env2=stress');
    });
});


