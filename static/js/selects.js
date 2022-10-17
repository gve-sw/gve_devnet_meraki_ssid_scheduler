$(function() {
    /*Show corresponding SSID list as soon as network is choosen in dropdown */
    $('#network_selection').bind('change', function() {
          $('#empty_ssid').attr("hidden", true);
          $('.ssid_selection').attr("hidden", true);
          var selectid = $( "#network_selection option:selected" ).val();
          $('#' + selectid).attr("hidden",false);       
      });                            
  });   

function checkTime(element) {
    var checkbox = element.parentElement.children[1]
    if (checkbox.checked) {
        checkbox.checked = false
    } else {
        checkbox.checked = true
    }
}

function selectSSID(element) {
    id = element.id.split('-')
    networkid = id[1]

    selected = document.getElementsByClassName('schedule_select')
    for (var i=0; i<selected.length;i++) {
        selected[i].hidden=true
    }

    var selected_ssid = element.options[element.selectedIndex].value;

    scheduleid = 'schedule' + networkid + '--' + selected_ssid
    document.getElementById(scheduleid).hidden = false
}

function loadSchedule(schedule) {
    var networks = document.getElementsByClassName('schedule_select')
    var selected_network = ''
    var selected_ssid = ''
    var dashIndex = 0
    for (var i=0; i<networks.length;i++) {
        if (!networks[i].hidden) {
            dashIndex = networks[i].id.indexOf('--')
            selected_network = networks[i].id.slice(8,dashIndex)
            selected_ssid = networks[i].id.slice(dashIndex+2, networks[i].id.length+1)
        }
    }
    schedule_clean = schedule.replaceAll("'", '"')
    schedule_json = JSON.parse(schedule_clean)

    var checkbox = ''
    var boxes = document.getElementsByClassName('active')
    var total = boxes.length
    const totalboxes = [...boxes]
    for (var j=0; j<total;j++) {
        checkbox = totalboxes[j].id.slice(2, totalboxes[j].id.length+1)
        document.getElementById('li' + checkbox).classList = []
        document.getElementById('check' + checkbox).checked = false
    }
    for (var i=0; i<schedule_json.length;i++) {
        checkbox = selected_network + "-" + selected_ssid + "-" + schedule_json[i]
        document.getElementById('li' + checkbox).classList = ['active']
        document.getElementById('check' + checkbox).checked = true
    } 
}