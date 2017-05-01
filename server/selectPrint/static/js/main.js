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
    if(data['ready']){
        
    }
    else{
        
    }
};
