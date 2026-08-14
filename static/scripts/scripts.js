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

        const $form = $modal.find('form').first();
        if ($form.length) {
            clearFormErrors($form);
            $form.trigger('reset');
        }

        $lastModalTrigger = null;
    }

    function setButtonLoading($btn, isLoading) {
        if (!$btn.length) {
            return;
        }

        if (isLoading) {
            const loadingText = $btn.data('loading-text');
            if (loadingText) {
                $btn.find('.btn-loading-text').text(loadingText);
            }
            $btn
                .prop('disabled', true)
                .attr('aria-busy', 'true')
                .addClass('is-loading');
            return;
        }

        $btn
            .prop('disabled', false)
            .removeAttr('aria-busy')
            .removeClass('is-loading');
    }

    function clearFormErrors($form) {
        $form.find('.form-errors').prop('hidden', true).empty();
        $form.find('.form-control').removeClass('is-invalid');
        $form.find('input, select, textarea').removeAttr('aria-invalid aria-describedby');
        $form.find('.form-control-wrapper > .error-msg').prop('hidden', true).empty();
    }

    function renderErrorList(messages) {
        const items = (Array.isArray(messages) ? messages : [messages])
            .filter(Boolean)
            .map((message) => $('<li></li>').text(message)[0].outerHTML)
            .join('');
        return items ? `<ul>${items}</ul>` : '';
    }

    function showFormErrors($form, errors) {
        clearFormErrors($form);
        if (!errors || typeof errors !== 'object') {
            return;
        }

        Object.entries(errors).forEach(([field, messages]) => {
            const html = renderErrorList(messages);
            if (!html) {
                return;
            }

            if (field === 'form') {
                $form.find('.form-errors').html(html).prop('hidden', false);
                return;
            }

            const $input = $form.find(`[name="${field}"]`);
            if (!$input.length) {
                $form.find('.form-errors').html(html).prop('hidden', false);
                return;
            }

            const errorId = `${field}-errors`;
            $input
                .attr('aria-invalid', 'true')
                .attr('aria-describedby', errorId)
                .closest('.form-control')
                .addClass('is-invalid');

            let $error = $form.find(`#${errorId}`);
            if (!$error.length) {
                $error = $('<div class="error-msg" role="alert"></div>').attr('id', errorId);
                $input.closest('.form-control-wrapper').append($error);
            }
            $error.html(html).prop('hidden', false);
        });
    }

    async function submitModalForm($modal, $confirmBtn) {
        const $form = $modal.find('form').first();
        if (!$form.length) {
            return;
        }

        const form = $form.get(0);
        if (typeof form.reportValidity === 'function' && !form.reportValidity()) {
            return;
        }

        clearFormErrors($form);
        setButtonLoading($confirmBtn, true);

        try {
            const response = await fetch($form.attr('action'), {
                method: ($form.attr('method') || 'POST').toUpperCase(),
                body: new FormData(form),
                headers: {
                    Accept: 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin',
            });

            let data = null;
            try {
                data = await response.json();
            } catch (err) {
                data = null;
            }

            if (!response.ok || !data || data.ok === false) {
                showFormErrors($form, (data && data.errors) || {
                    form: ['Something went wrong. Please try again.'],
                });
                return;
            }

            closeModal($modal);
            if (data.redirect_url) {
                window.location.href = data.redirect_url;
            }
        } catch (err) {
            showFormErrors($form, {
                form: ['Something went wrong. Please try again.'],
            });
        } finally {
            setButtonLoading($confirmBtn, false);
        }
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

    $(document).on('click', '.modal-confirm', function () {
        const $confirmBtn = $(this);
        const $modal = $confirmBtn.closest('.overlay');
        const action = $modal.data('confirm');

        if (action === 'submit-form') {
            submitModalForm($modal, $confirmBtn);
        }
    });

    $(document).on('submit', '.overlay[data-confirm="submit-form"] form', function (e) {
        e.preventDefault();
        const $modal = $(this).closest('.overlay');
        submitModalForm($modal, $modal.find('.modal-confirm').first());
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
