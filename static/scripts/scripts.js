$(document).ready(function(){
    
    /**
     * Options button
     */
    $('#options-toggler').click(() => {
        const $toggler = $('#options-toggler');
        const $options = $('#options');
        const isOpen = $toggler.attr('aria-expanded') === 'true';

        $toggler.attr('aria-expanded', String(!isOpen));

        if (isOpen) {
            $options
                .removeClass('options-opening')
                .addClass('options-closing')
                .one('animationend', () => {
                    $options.hide().removeClass('options-closing');
                });
        } else {
            $options
                .show()
                .removeClass('options-closing')
                .addClass('options-opening');
        }
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

    function closeAllNoteEdits() {
        $('.note-slot').each(function () {
            const $slot = $(this);
            const $form = $slot.find('.note-form');
            $slot.find('.error-msg').html('');
            $form.trigger('reset');
            $slot.find('.note-edit').addClass('hidden-form');
            $slot.find('.note-view').removeClass('hidden-form');
        });
    }

    function closeAddNoteForm() {
        const $addForm = $('#addNoteForm');
        $addForm.find('.error-msg').html('');
        $addForm.find('.note-form').trigger('reset');
        $addForm.addClass('hidden-form');
    }

    /**
     * Edit note button
     */
    $(document).on('click', '.edit-btn', function () {
        const $slot = $(this).closest('.note-slot');
        if (!$slot.length) {
            return;
        }
        closeAddNoteForm();
        closeAllNoteEdits();
        $slot.find('.note-view').addClass('hidden-form');
        $slot.find('.note-edit').removeClass('hidden-form');
    });


    /**
     * Note form validation (add + edit)
     */
    $(document).on('submit', '.note-form', function (e) {
        const $form = $(this);
        const title = $form.find('.note-title').val();
        const errorField = $form.find('.error-msg');
        let errors = [];

        if (title === "" || title === null) {
            errors.push("A title is required.");
        }
        if (errors.length > 0) {
            e.preventDefault();
            errorField.html(errors.join('<br>'));
        }
    });

    /**
     * 
     * Cancel note form (add + edit)
     */
    $(document).on('click', '.note-form-button-cancel', function () {
        const $form = $(this).closest('.note-form');
        const $slot = $(this).closest('.note-slot');

        $form.find('.error-msg').html('');
        $form.trigger('reset');

        if ($slot.length) {
            $slot.find('.note-edit').addClass('hidden-form');
            $slot.find('.note-view').removeClass('hidden-form');
        } else {
            $('#addNoteForm').addClass('hidden-form');
        }
    });

    /**
     * 
     * Add note button
     */
    $('#addNoteButton').click( () => {
        closeAllNoteEdits();
        $('#addNoteForm').removeClass('hidden-form');
    });
});
