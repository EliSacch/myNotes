$(document).ready(function(){
    /**
     * Page transitions (dashboard switches and same-origin navigations)
     */
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const PAGE_EXIT_MS = 280;
    const PAGE_TRANSITION_KEY = 'pinit-page-transition';

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
            $('#dashboards-toggler')
                .attr('aria-expanded', 'false')
                .attr('aria-label', 'Open dashboards');
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

    function setButtonLoading($btn, isLoading) {
        if (!$btn.length) {
            return;
        }

        const $label = $btn.find('.btn-label');
        const $loading = $btn.find('.btn-loading');

        if (isLoading) {
            const loadingText = $btn.data('loading-text') || 'Loading...';
            $btn.find('.btn-loading-text').text(loadingText);
            $label.attr('hidden', true);
            $loading.removeAttr('hidden');
            $btn
                .prop('disabled', true)
                .attr('aria-busy', 'true')
                .addClass('is-loading');
            return;
        }

        $label.removeAttr('hidden');
        $loading.attr('hidden', true);
        $btn
            .prop('disabled', false)
            .removeAttr('aria-busy')
            .removeClass('is-loading');
    }

    function formSubmitButtons($form) {
        return $form.find('button.base-button').filter(function () {
            const type = (this.getAttribute('type') || 'submit').toLowerCase();
            return type === 'submit';
        });
    }

    $(document).on('submit', 'form', function (event) {
        const $form = $(this);
        const submitter = event.originalEvent && event.originalEvent.submitter;
        let $btn = submitter ? $(submitter) : $();
        if (!$btn.is('button.base-button')) {
            $btn = formSubmitButtons($form);
        }
        if (!$btn.length) {
            return;
        }
        if ($btn.filter(':disabled').length === $btn.length) {
            return false;
        }

        setButtonLoading($btn, true);
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

    function setModalTerminalState($modal, isTerminal) {
        const $confirm = $modal.find('.modal-confirm');
        const $cancelLabel = $modal.find('.modal-footer .modal-close .btn-label');

        if (isTerminal) {
            $modal.addClass('is-terminal').attr('role', 'alertdialog');
            $confirm.prop('disabled', true);
            $cancelLabel.text('Close');
            return;
        }

        $modal.removeClass('is-terminal').attr('role', 'dialog');
        $confirm.prop('disabled', false);
        $cancelLabel.text('Cancel');
    }

    function openModal($modal, $trigger) {
        $lastModalTrigger = $trigger || null;
        setModalTerminalState($modal, false);

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

        setModalTerminalState($modal, false);
        $lastModalTrigger = null;
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
        if (!$form.length || $modal.hasClass('is-terminal')) {
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
                setButtonLoading($confirmBtn, false);
                if (data && data.retryable === false) {
                    setModalTerminalState($modal, true);
                }
                focusFormErrors($form);
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
            focusFormErrors($form);
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

    const $modalWithErrors = $('.overlay').filter(function () {
        return $(this).find('.error-msg[role="alert"]:not([hidden]), .form-errors[role="alert"]:not([hidden])').length;
    }).first();
    if ($modalWithErrors.length) {
        openModal($modalWithErrors);
        focusFormErrors($modalWithErrors.find('form').first());
    }

    $(document).on('click', '.modal-close', function () {
        const $overlay = $(this).closest('.overlay');
        if ($overlay.length) {
            closeModal($overlay);
        }
    });

    $(document).on('click', '.modal-confirm', function () {
        const $confirmBtn = $(this);
        if ($confirmBtn.prop('disabled')) {
            return;
        }

        const $modal = $confirmBtn.closest('.overlay');
        const action = $modal.data('confirm');

        if (action === 'submit-form') {
            submitModalForm($modal, $confirmBtn);
        } else if (action === 'logout') {
            setButtonLoading($confirmBtn, true);
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
            return;
        }
        if ($('#options-toggler').attr('aria-expanded') === 'true') {
            closeOptionsMenu(true);
            return;
        }
        if ($('#dashboards-toggler').attr('aria-expanded') === 'true') {
            closeDashboardsMenu(true);
        }
    });

    /**
     * Options / dashboards disclosures
     */
    function closeOptionsMenu(returnFocus) {
        const $toggler = $('#options-toggler');
        const $options = $('#options');
        if ($toggler.attr('aria-expanded') !== 'true') {
            return;
        }

        $toggler.attr('aria-expanded', 'false');
        $toggler.attr('aria-label', 'Open options');
        $options.removeClass('options-opening');

        if (prefersReducedMotion) {
            $options.hide().removeClass('options-closing');
        } else {
            $options
                .addClass('options-closing')
                .one('animationend', () => {
                    $options.hide().removeClass('options-closing');
                });
        }

        if (returnFocus) {
            $toggler.trigger('focus');
        }
    }

    function openOptionsMenu() {
        const $toggler = $('#options-toggler');
        const $options = $('#options');

        $toggler.attr('aria-expanded', 'true');
        $toggler.attr('aria-label', 'Close options');
        $options
            .show()
            .removeClass('options-closing')
            .addClass('options-opening');

        const $firstAction = $options.find('button').first();
        if ($firstAction.length) {
            $firstAction.trigger('focus');
        }
    }

    function closeDashboardsMenu(returnFocus) {
        const $toggler = $('#dashboards-toggler');
        const $list = $('#dashboards-list');
        if ($toggler.attr('aria-expanded') !== 'true') {
            return;
        }

        $toggler.attr('aria-expanded', 'false');
        $toggler.attr('aria-label', 'Open dashboards');
        $list.removeClass('dashboards-opening');

        if (prefersReducedMotion) {
            $list.hide().removeClass('dashboards-closing');
        } else {
            $list
                .addClass('dashboards-closing')
                .one('animationend', () => {
                    $list.hide().removeClass('dashboards-closing');
                });
        }

        if (returnFocus) {
            $toggler.trigger('focus');
        }
    }

    function openDashboardsMenu() {
        const $toggler = $('#dashboards-toggler');
        const $list = $('#dashboards-list');

        $toggler.attr('aria-expanded', 'true');
        $toggler.attr('aria-label', 'Close dashboards');
        $list
            .show()
            .removeClass('dashboards-closing')
            .addClass('dashboards-opening');

        const $firstLink = $list.find('a').first();
        if ($firstLink.length) {
            $firstLink.trigger('focus');
        }
    }

    function focusNoteForm($form) {
        if (!$form || !$form.length) {
            return;
        }
        const title = $form.find('.note-title').get(0);
        if (!title) {
            return;
        }
        // Defer past the activating keyup/click and layout from un-hiding the form.
        // Same-turn focus from a button often leaves the input visually focused but not editable.
        window.requestAnimationFrame(function () {
            window.requestAnimationFrame(function () {
                title.focus({ preventScroll: true });
                if (typeof title.setSelectionRange === 'function') {
                    const len = title.value.length;
                    title.setSelectionRange(len, len);
                }
            });
        });
    }

    function focusFormErrors($form) {
        if (!$form || !$form.length) {
            return;
        }
        const $invalid = $form.find('[aria-invalid="true"]').first();
        if ($invalid.length) {
            $invalid.trigger('focus');
            return;
        }
        const $alert = $form.find('.error-msg[role="alert"]:not([hidden]), .form-errors[role="alert"]:not([hidden])').first();
        if ($alert.length) {
            if (!$alert.attr('tabindex')) {
                $alert.attr('tabindex', '-1');
            }
            $alert.trigger('focus');
        }
    }

    /**
     * Options button
     */
    $('#options-toggler').click(() => {
        const isOpen = $('#options-toggler').attr('aria-expanded') === 'true';
        if (isOpen) {
            closeOptionsMenu(false);
        } else {
            closeDashboardsMenu(false);
            openOptionsMenu();
        }
    });

    /**
     * Dashboards toggler
     */
    $('#dashboards-toggler').click(() => {
        const isOpen = $('#dashboards-toggler').attr('aria-expanded') === 'true';
        if (isOpen) {
            closeDashboardsMenu(false);
        } else {
            closeOptionsMenu(false);
            openDashboardsMenu();
        }
    });

    $(document).on('click', function (event) {
        const $target = $(event.target);
        if (!$target.closest('#options-nav').length) {
            closeOptionsMenu(false);
        }
        if (!$target.closest('#dashboards-nav').length) {
            closeDashboardsMenu(false);
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
            const $form = $slot.find('.note-form');
            const initPromise =
                window.NoteEditor && typeof window.NoteEditor.init === 'function'
                    ? window.NoteEditor.init($form)
                    : Promise.resolve();
            return Promise.resolve(initPromise).then(function () {
                focusNoteForm($form);
            });
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
                $slot.find('.edit-btn').first().trigger('focus');
            } else {
                $('#addNoteForm').addClass('hidden-form');
                $('#addNoteButton').trigger('focus');
            }
        });
    });

    /**
     * Add note button
     */
    $('#addNoteButton').click( () => {
        closeOptionsMenu(false);
        closeAllNoteEdits().then(function () {
            const $addForm = $('#addNoteForm');
            $addForm.removeClass('hidden-form');
            const $form = $addForm.find('.note-form');
            const initPromise =
                window.NoteEditor && typeof window.NoteEditor.init === 'function'
                    ? window.NoteEditor.init($form)
                    : Promise.resolve();
            return Promise.resolve(initPromise).then(function () {
                focusNoteForm($form);
            });
        });
    });
});
