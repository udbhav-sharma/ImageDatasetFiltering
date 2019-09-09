currentImage = {"id" : ""};
index = 1;

$( document ).ready(function() {
    index = initIndex();
    updateImage(currentIndex(), function(){}, function (){});
});

$( "#prevBtn" ).click(function() {
    if (currentIndex() > 1) {
        updateImage(decrementIndex(), function(){}, function () {
            incrementIndex();
        });
    }
});

$( "#yesBtn" ).click(function() {
    updateStatus(currentImage.id, 1, function() {
        updateImage(incrementIndex(), function(){}, function () {
            decrementIndex();
        });
    });
});

$( "#noBtn" ).click(function() {
    updateStatus(currentImage.id, 0, function() {
        updateImage(incrementIndex(), function(){}, function () {
            decrementIndex();
        });
    });
});

$('#exportBtn').click(function() {
    var name = prompt("Please enter dataset name. Special characters are not allowed.");
    name = name.replace(/[^a-zA-Z0-9]/g,'');

    if (name.length < 0) {
        showError("Invalid dataset name");
        return;
    }

    disableAll();
    $.ajax({
        url: "/dataset/" + getDatasetName() + "/export",
        type: 'POST',
        data: {
            "name": name
        },
        success: function(response) {
            enableAll();
            showSuccess("Dataset " + response + " exported successfully!!");
        },
        error: function(response) {
            showError("Something went wrong...");
            enableAll();
        }
     });
});

function initIndex() {
    index_str = window.location.hash.substr(1);
    if (index_str != "" && !isNaN(index_str)) 
        return Math.max(1, parseInt(index_str));
    
    return 1;
}

function currentIndex() {
    return index;
}

function incrementIndex() {
    index++;
    return index;
}

function decrementIndex() {
    index = Math.max(1, index-1);
    return index;
}

function updateImage(index, successCallback, errCallback) {
    disableAll();
    $.get( "/dataset/" + getDatasetName() + "/" + index, function( data ) {
        currentImage = data;
        enableAll();
        showImage();
        successCallback();
    }).fail(function() {
        enableAll();
        showError("Something went wrong...");
        errCallback();
    });
}

function updateStatus(id, status, successCallback) {
    disableAll();
    $.ajax({
        url: "/dataset/" + getDatasetName() + "/status/" + id + "/" + status,
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

function showImage() {
    if (currentImage.id == "<END>") {
        $('#prevBtn').hide();
        $('#image-selection-container').hide();
        $('#image-selection-completion-container').show();
    }
    else {
        $('#image-details').html(getImageDetails());
        $('#image-status-div').html(getImageStatusDiv());
        $('#image-div').html(getImageDiv()); 
    }
}

function getImageDetails() {
    html = currentImage.id;

    if (currentImage.category.length >= 1) {
        html += ": " + currentImage.category.join(" -> ");
    }

    return html;
}

function getImageStatusDiv() {
    if (currentImage.status == 1)
        return '<span class="badge badge-pill badge-success float-right">Selected</span>';

    return '<span class="badge badge-pill badge-danger float-right">Not Selected</span>';

}

function getImageDiv() {
    url = "/static/dataset/" + getDatasetName() + "/images/" + currentImage.name;
    return $('<img src="' + url + '" style="width:100%; height:auto;" />')
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
