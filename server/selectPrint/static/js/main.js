
$(document).ready(function () {

  $("#carousel").owlCarousel({
    //navigation: true, // Show next and prev buttons
    slideSpeed: 300,
    paginationSpeed: 400,
    singleItem: true
  });

});

printerStateCallback = function (data) {
  data = JSON.parse(data);
  if (data['ready']) {

  }
  else {

  }
};

function loadAndPrint(fileName, index) {
  var formData = new FormData();
  console.log($('.printerSelect'))
  formData.append('selectedPrinters',$($('.printerSelect')[index-1]).find(':selected').val());

  $.ajax({
    url: '/api/load/'+fileName,
    type: 'POST',
    processData: false,
    contentType: false,
    data: formData,
    success: function (data) {
      data = JSON.parse(data);
      console.log(data)
      if(data[0][1] == 204) {
        alert('successful');
      }
      else {
        alert(data[0][0]);
      }
    }
  })
}

function getPrinters() {
  $.ajax({
    url: '/api/printer-config',
    type: 'GET',
    success: function (data){
      data = JSON.parse(data);
      var printerSelect = $('.printerSelect');
      printerSelect.append();
      $.each(data.printers,function (index, value) {
        printerSelect.append($('<option></option>').attr('value',index).text(value.name));
      });

    }
  })
}

getPrinters();