var current_document;

function showDocument(id) {
    $.ajax({
        url:"/resolver/document/"+id+".json",
        dataType:"json",
        success: function (data) {
            if(!data.errors) {
                current_document = id;

                $("#editUrl").val(data.url);
                $("#editType").val(data.type);
                $("#editEnabled").prop('checked', data.enabled);
                $("#editNotes").val(data.notes);

                $("#docModal").modal('show');

                if(data.url && !data.resolves) {
                    $("#resolveAlert").show();
                } else {
                    $("#resolveAlert").hide();
                }
            }}});
}

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
