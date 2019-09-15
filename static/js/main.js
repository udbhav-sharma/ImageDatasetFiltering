currentImage = {"id" : ""};

$( document ).ready(function() {
    window.onhashchange = function() {
        updateImage(currentIndex());
    }

    updateImage(currentIndex());
});

$( "#prevBtn" ).click(function() {
    window.location.hash = decrementIndex();
});

$( "#yesBtn" ).click(function() {
    updateStatus(currentImage.id, 1, function() {
        window.location.hash = incrementIndex();
    });
});

$( "#mayBeBtn" ).click(function() {
    updateStatus(currentImage.id, 2, function() {
        window.location.hash = incrementIndex();
    });
});

$( "#noBtn" ).click(function() {
    updateStatus(currentImage.id, 0, function() {
        window.location.hash = incrementIndex();
    });
});

$('#exportBtn').click(function() {
    var name = prompt("Please enter dataset name. Special characters are not allowed.");
    name = name.replace(/[^a-zA-Z0-9-_]/g, '');

    if (name.length < 0) {
        showError("Invalid dataset name");
        return;
    }

    disableAll();
    $.ajax({
        url: "/api/dataset/" + getDatasetName() + "/export",
        type: 'POST',
        data: {
            "name": name
        },
        success: function(response) {
            enableAll();
            showSuccess("Dataset " + response + " exported successfully!!");
        },
        error: function(response) {
            showError(response.responseText);
            enableAll();
        }
     });
});

function currentIndex() {
    return getIndexFromUrl();
}

function incrementIndex() {
    return currentIndex() + 1;
}

function decrementIndex() {
    return Math.max(1, currentIndex() - 1);
}

function updateImage(index) {
    disableAll();
    $.get( "/api/dataset/" + getDatasetName() + "/" + index, function( data ) {
        currentImage = data;
        enableAll();
        showImage(currentImage);
    }).fail(function() {
        enableAll();
        showError("Something went wrong...");
    });
}

function updateStatus(id, status, successCallback) {
    disableAll();
    $.ajax({
        url: "/api/dataset/" + getDatasetName() + "/status/" + id + "/" + status,
        type: 'PUT',
        success: function(response) {
            enableAll();
            successCallback();
        },
        error: function(response) {
            showError("Something went wrong...");
            enableAll();
        }
     });
}

function disableAll() {
    $('.btn').attr("disabled", true);	
}

function enableAll() {
    $('.btn').attr("disabled", false);	
}

function showImage(image) {
    if (image.id == "<END>") {
        $('#prevBtn').hide();
        $('#image-selection-container').hide();
        $('#image-selection-completion-container').show();
    }
    else {
        $('#image-details').html(generateImageDetails(image));
        $('#image-status-div').html(generateImageStatusDiv(image));
        $('#image-div').html(generateImageDiv(image)); 
    }
}

function generateImageDetails(image) {
    html = image.id;

    if (image.category.length >= 1) {
        html += ": " + image.category.join(" -> ");
    }

    return html;
}

function generateImageStatusDiv(image) {
    if (image.status == 1)
        return '<span class="badge badge-pill badge-success float-right">Selected</span>';
    else if (image.status == 2)
        return '<span class="badge badge-pill badge-warning float-right">Needs Fixing</span>';

    return '<span class="badge badge-pill badge-danger float-right">Not Selected</span>';

}

function generateImageDiv(image) {
    url = "/static/dataset/" + getDatasetName() + "/images/" + image.name;
    return $('<img src="' + url + '" style="width: auto; height:100%;" />')
            .click(function(){
                window.open(url, '_blank');
            });
}

function showSuccess(msg) {
    $.notify({
        message: msg 
    },{
        type: 'success',
        delay: 3000
    });
}

function showError(errMsg) {
    $.notify({
        message: errMsg 
    },{
        type: 'danger',
        delay: 3000
    });
}

function getDatasetName() {
    var l = document.createElement("a");
    l.href = window.location.href;
    return l.pathname.split("/")[2];
}

function getIndexFromUrl() {
    index_str = window.location.hash.substr(1);
    if (index_str != "" && !isNaN(index_str)) 
        return Math.max(1, parseInt(index_str));
    
    return 1;
}
