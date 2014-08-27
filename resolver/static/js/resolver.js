var current_document;
var action;

function confirmDelete(url) {
    var c = confirm('Are you sure?');
    if(c) {
        window.location.href = url;
    }
}

function showDocument(id) {
    $.ajax({
        url:"/resolver/document/"+id+".json",
        dataType:"json",
        success: function (data) {
            if(!data.errors) {
                current_document = id;
                action = base_url + '/resolver/document/edit/'+id+'.json';

                $("#btnMSubmit").html('Save');
                $("#btnDelete").show();

                $("#editUrl").val(data.url);
                $("#editEnabled").prop('checked', data.enabled);
                $("#editNotes").val(data.notes);

                if(data.type == 'data') {
                    $("#dataInputs").show();
                    $("#representationInputs").hide();
                    $("#dataFormat").val(data.format);
                } else {
                    $("#dataInputs").hide();
                    $("#representationInputs").show();
                    $("#representation Reference").prop('checked', data.reference);
                }

                if(data.url && !data.resolves) {
                    $("#resolveAlert").show();
                } else {
                    $("#resolveAlert").hide();
                }

                $("#docModal").modal('show');
            }}});
}

function prepForm(){
    $("#resolveAlert").hide();
    $("#btnMSubmit").html('Add');
    $("#editErrors").empty();
    $("#btnDelete").hide();
    $("#docEditForm")[0].reset();
}

$('.link-delete-entity').click(function(event) {
    url = '/resolver/entity/delete/'+event.currentTarget.id;
    confirmDelete(url);
});

$("#btnMDelete").click(function(event){
    if(current_document){
        confirmDelete('/resolver/document/delete/'+current_document);
    }
});

$("#btnDataAdd").click(function(event){
    edit_mode=false;
    prepForm();
    $("#dataInputs").show();
    $("#representationInputs").hide();
    $("#docModal").modal('show');
    action = base_url + '/resolver/document/data/'+entity_id;
});

$("#btnRepresentationAdd").click(function(event){
    edit_mode=false;
    prepForm();
    $("#dataInputs").hide();
    $("#representationInputs").show();
    $("#docModal").modal('show');
    action = base_url + '/resolver/document/representation/'+entity_id;
});

$("#btnMSubmit").click(function(event){
    $("#docEditForm").submit();
});

$("#docEditForm").submit(function(event){
    $("#editErrors").empty();
    $.post(action,
           $("#docEditForm").serialize(),
           function(data){
               if(data.errors) {
                   for(var i = 0; i<data.errors.length; i++){
                       $("#editErrors").append('<div class="alert alert-danger"><strong>'+data.errors[i].title+'</strong> '+data.errors[i].detail+'</div>');
                   }
               } else {
                   location.reload();
               }
           }, 'json');
});
