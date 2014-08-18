var current_document;

function showDocument(id) {
    $.ajax({
        url:"/resolver/document/"+id+".json",
        dataType:"json",
        success: function (data) {
            if(!data.errors) {
                current_document = id;

                $("#docModalType").text(data.type);
                $("#docModalEnabled").text(data.enabled);
                $("#docModalURL").text(data.url);
                $("#docModalPURI").text(data.persistent_uri);
                $("#docModalNotes").text(data.notes);

                $("#editUrl").val(data.url);
                $("#editType").val(data.type);
                $("#editEnabled").prop('checked', data.enabled);
                $("#editNotes").val(data.notes);

                $("#docModalDetails").show();
                $("#docModalForm").hide();
                $("#btnEdit").show();
                $("#docModal").modal('show');

                if(data.url && !data.resolves) {
                    $("#resolveAlert").show();
                } else {
                    $("#resolveAlert").hide();
                }
            }}});
}

function toggleForm() {
    $("#editErrors").empty();
    $("#docModalDetails").toggle();
    $("#docModalForm").toggle();
    $("#btnEdit").toggle();
}

$("#btnEdit").click(toggleForm);
$("#btnCancel").click(toggleForm);

$("#btnDelete").click(function(event){
    window.location.href = '/resolver/document/delete/'+current_document;
});

$("#docEditForm").submit(function(event){
    $("#editErrors").empty();
    $.post('/resolver/document/edit/'+current_document+'.json',
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
