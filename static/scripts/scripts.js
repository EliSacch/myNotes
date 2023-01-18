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
     * Add list items functions
     */

    $('#addItem').attr("disabled", true)
    /* Disable add item button if empty input */
    $('#content').on('input', () => {
        isEmpty = $('#content').val().length == 0
        if(!isEmpty) {
            $('#addItem').attr("disabled", false)
        } else {
            $('#addItem').attr("disabled", true)
        }
    })

    items = []

    /* Add list item button */
    $('#addItem').click( () => {
        itemId = 0
        itemValue = $('#content').val()
        items.push(itemValue)
        displayItems()
        $('#content').val('')
        $('#addItem').attr("disabled", true)

        /* Remove list item button */
        $('.deleteItem').on("click", deleteItem)
    });

    /* Delete list item */
    function deleteItem() {
        itemId = $(this).attr('data-id')
        items.splice(itemId,1)
        displayItems()
    }

    /* Display added items */
    function displayItems() {
        display = $('.displayItems')
        display.html("")
        for(item of items) {
            display.append(`<span class="list-item"><button class="deleteItem" data-id="${items.indexOf(item)}" type="button">X</button><p>${item}</p></span>`)
        }
    } 


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


    /**
     * Add note and list form validation
     */
    $('#addNew').submit( (e) => {
        let errors = []
        const title = $('#title')
        const content = $('#content')
        const errorField = $('#errorMsg')

        if(title.val() === "" || title.val() === null) {
            errors.push('A title is required.')
        }

        if(content.val() === "" || content.val() === null) {
            errors.push('Some content is required.')
        }

        if (errors.length > 0) {
            e.preventDefault()
            errorField.html(errors.join('<br>'))
        }
    })

});



