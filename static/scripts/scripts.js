$(document).ready(function(){
    
    /**
     * Options button
     */
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


    /**
     * Edit note button
     */
    $('.edit-btn').click( () => {
        console.log('edit')
    });


    /**
     * 
     * Delete note button
     */
    $('.delete-btn').click( () => {
        console.log('delete')
    });


});