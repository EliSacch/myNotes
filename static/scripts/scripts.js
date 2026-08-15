$(document).ready(function(){
    /**
     * Page transitions (dashboard switches and same-origin navigations)
     */
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const PAGE_EXIT_MS = 280;
    const PAGE_TRANSITION_KEY = 'mynotes-page-transition';

    function markPageTransitionTargets() {
        $('main, .form-wrapper, .error-page').addClass('page-transition-target');
    }

    function clearPendingTransitionFlag() {
        try {
            sessionStorage.removeItem(PAGE_TRANSITION_KEY);
        } catch (err) {
            /* ignore */
        }
        document.documentElement.classList.remove('is-page-pending');
    }

    function playPageEnter() {
        const shouldEnter = document.documentElement.classList.contains('is-page-pending');
        clearPendingTransitionFlag();
        markPageTransitionTargets();

        if (!shouldEnter || prefersReducedMotion) {
            $('body').removeClass('is-page-entering is-page-exiting');
            return;
        }

        $('body').removeClass('is-page-exiting').addClass('is-page-entering');
        window.setTimeout(() => {
            $('body').removeClass('is-page-entering');
        }, 500);
    }

    function navigateWithTransition(url) {
        if (!url || prefersReducedMotion || $('body').hasClass('is-page-exiting')) {
            window.location.href = url;
            return;
        }

        try {
            sessionStorage.setItem(PAGE_TRANSITION_KEY, '1');
        } catch (err) {
            /* ignore */
        }

        const $dashboardsList = $('#dashboards-list');
        if ($dashboardsList.is(':visible')) {
            $('#dashboards-toggler').attr('aria-expanded', 'false');
            $dashboardsList
                .hide()
                .removeClass('dashboards-opening dashboards-closing');
        }

        markPageTransitionTargets();
        $('body').removeClass('is-page-entering').addClass('is-page-exiting');

        let navigated = false;
        const go = () => {
            if (navigated) {
                return;
            }
            navigated = true;
            window.location.href = url;
        };

        $('.page-transition-target').first().one('animationend', go);
        window.setTimeout(go, PAGE_EXIT_MS + 80);
    }

    function shouldInterceptNavigation(event, anchor) {
        if (event.defaultPrevented) {
            return false;
        }
        if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
            return false;
        }
        if (anchor.target && anchor.target !== '_self') {
            return false;
        }
        if (anchor.hasAttribute('download')) {
            return false;
        }

        let url;
        try {
            url = new URL(anchor.href, window.location.href);
        } catch (err) {
            return false;
        }

        if (url.origin !== window.location.origin) {
            return false;
        }
        if (url.pathname === window.location.pathname && url.search === window.location.search) {
            return false;
        }
        // Same-page hash jumps should stay instant.
        if (url.pathname === window.location.pathname && url.hash) {
            return false;
        }

        return true;
    }

    playPageEnter();

    $(window).on('pageshow', function (event) {
        if (event.originalEvent && event.originalEvent.persisted) {
            clearPendingTransitionFlag();
            $('body').removeClass('is-page-entering is-page-exiting');
            markPageTransitionTargets();
        }
    });

    $(document).on('click', 'a[href]', function (event) {
        const anchor = this;
        if (!shouldInterceptNavigation(event, anchor)) {
            return;
        }

        event.preventDefault();
        navigateWithTransition(anchor.href);
    });

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

        if (!$modal.parent().is('body')) {
            $modal.appendTo(document.body);
        }

        const formAction = $trigger && $trigger.attr('data-form-action');
        if (formAction) {
            $modal.find('form').first().attr('action', formAction);
        }

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
                navigateWithTransition(data.redirect_url);
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
        } else if (action === 'logout') {
            window.location.href = '/logout';
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

    /**
     * Dashboards toggler
     */
    $('#dashboards-toggler').click(() => {
        const $toggler = $('#dashboards-toggler');
        const $options = $('#dashboards-list');
        const isOpen = $toggler.attr('aria-expanded') === 'true';

        $toggler.attr('aria-expanded', String(!isOpen));

        if (isOpen) {
            $options
                .removeClass('dashboards-opening')
                .addClass('dashboards-closing')
                .one('animationend', () => {
                    $options.hide().removeClass('dashboards-closing');
                });
        } else {
            $options
                .show()
                .removeClass('dashboards-closing')
                .addClass('dashboards-opening');
        }
    });

    function closeAllNoteEdits() {
        const destroyPromises = [];
        $('.note-slot').each(function () {
            const $slot = $(this);
            const $form = $slot.find('.note-form');
            $slot.find('.error-msg').html('');
            if (window.NoteEditor && typeof window.NoteEditor.destroy === 'function') {
                destroyPromises.push(window.NoteEditor.destroy($form));
            }
            $form.trigger('reset');
            $slot.find('.note-edit').addClass('hidden-form');
            $slot.find('.note-view').removeClass('hidden-form');
        });
        return Promise.all(destroyPromises);
    }

    function closeAddNoteForm() {
        const $addForm = $('#addNoteForm');
        const $form = $addForm.find('.note-form');
        $addForm.find('.error-msg').html('');
        let destroyPromise = Promise.resolve();
        if (window.NoteEditor && typeof window.NoteEditor.destroy === 'function') {
            destroyPromise = window.NoteEditor.destroy($form);
        }
        $form.trigger('reset');
        $addForm.addClass('hidden-form');
        return destroyPromise;
    }

    /**
     * Edit note button
     */
    $(document).on('click', '.edit-btn', function () {
        const $slot = $(this).closest('.note-slot');
        if (!$slot.length) {
            return;
        }
        Promise.all([closeAddNoteForm(), closeAllNoteEdits()]).then(function () {
            $slot.find('.note-view').addClass('hidden-form');
            $slot.find('.note-edit').removeClass('hidden-form');
            if (window.NoteEditor && typeof window.NoteEditor.init === 'function') {
                window.NoteEditor.init($slot.find('.note-form'));
            }
        });
    });

    /**
     * Cancel note form (add + edit)
     */
    $(document).on('click', '.note-form-button-cancel', function () {
        const $form = $(this).closest('.note-form');
        const $slot = $(this).closest('.note-slot');

        $form.find('.error-msg').html('');
        const destroyPromise =
            window.NoteEditor && typeof window.NoteEditor.destroy === 'function'
                ? window.NoteEditor.destroy($form)
                : Promise.resolve();

        destroyPromise.then(function () {
            $form.trigger('reset');
            if ($slot.length) {
                $slot.find('.note-edit').addClass('hidden-form');
                $slot.find('.note-view').removeClass('hidden-form');
            } else {
                $('#addNoteForm').addClass('hidden-form');
            }
        });
    });

    /**
     * Add note button
     */
    $('#addNoteButton').click( () => {
        closeAllNoteEdits().then(function () {
            const $addForm = $('#addNoteForm');
            $addForm.removeClass('hidden-form');
            if (window.NoteEditor && typeof window.NoteEditor.init === 'function') {
                window.NoteEditor.init($addForm.find('.note-form'));
            }
        });
    });
});
