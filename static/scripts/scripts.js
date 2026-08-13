$(document).ready(function(){

    /**
     * Auth form submit loading state
     */
    $(document).on('submit', '#register, #login', function () {
        const $btn = $(this).find('.form-submit-btn');
        if ($btn.prop('disabled')) {
            return false;
        }

        const loadingText = $btn.data('loading-text');
        if (loadingText) {
            $btn.find('.btn-loading-text').text(loadingText);
        }

        $btn
            .prop('disabled', true)
            .attr('aria-busy', 'true')
            .addClass('is-loading');
    });

    /**
     * Modal open / close
     * Page behind the dialog is inert while open; dialog is inert while closed.
     * Move focus out before hiding so AT users aren't trapped in aria-hidden.
     */
    let $lastModalTrigger = null;

    function setBackgroundInert(isInert) {
        $('body').children().not('.overlay').each(function () {
            if (isInert) {
                $(this).attr('inert', '');
            } else {
                $(this).removeAttr('inert');
            }
        });
    }

    function openModal($modal, $trigger) {
        $lastModalTrigger = $trigger || null;
        setBackgroundInert(true);

        $modal
            .removeAttr('inert')
            .attr('aria-hidden', 'false')
            .addClass('visible');

        const $focusTarget = $modal.find('.modal-close, button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])').filter(':visible').first();
        if ($focusTarget.length) {
            $focusTarget.trigger('focus');
        }
    }

    function closeModal($modal) {
        // Clear page inert first so the trigger can receive focus again.
        setBackgroundInert(false);

        const $returnFocus = $lastModalTrigger && $lastModalTrigger.length
            ? $lastModalTrigger
            : $('.modal-trigger').filter('[data-modal="' + $modal.attr('id') + '"]').first();

        if ($returnFocus.length) {
            $returnFocus.trigger('focus');
        } else if (document.activeElement && $modal[0].contains(document.activeElement)) {
            document.activeElement.blur();
        }

        $modal
            .removeClass('visible')
            .attr('aria-hidden', 'true')
            .attr('inert', '');

        $lastModalTrigger = null;
    }

    $(document).on('click', '.modal-trigger', function () {
        const $trigger = $(this);
        const $modal = $(`#${$trigger.attr('data-modal')}`);
        if ($modal.length) {
            openModal($modal, $trigger);
        }
    });

    $(document).on('click', '.modal-close', function () {
        const $overlay = $(this).closest('.overlay');
        if ($overlay.length) {
            closeModal($overlay);
        }
    });

    $(document).on('keydown', function (e) {
        if (e.key !== 'Escape') {
            return;
        }
        const $openModal = $('.overlay.visible').last();
        if ($openModal.length) {
            closeModal($openModal);
        }
    });
    
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
