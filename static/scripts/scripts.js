$(document).ready(function(){
    
    $('#options-toggler').click( () => {
        $('#options').slideToggle();
        $('#options-toggler').attr('aria-expanded', (i, attr) => {
            if(attr == 'false') {
                return 'true'
            } else {
                return 'false'
            }
        })
    });
});