(function () {
    var utils = {
        getIcon: function (question) {
            if (question.tag === 'upload') {
                return '<i class="fa fa-paperclip"></i> ';
            }
            return '';
        },
        getDisplay: function (question, MAXLEN) {
            return utils.getIcon(question) + utils.getLabel(question, MAXLEN)
                    + " (" + (question.hashtagValue || question.value) + ")";
        },
        getTruncatedDisplay: function (question, MAXLEN) {
            return utils.getIcon(question) + utils.getLabel(question, MAXLEN)
                    + " (" + utils.truncateValue(question.hashtagValue || question.value, MAXLEN) + ")";
        },
        getLabel: function (question, MAXLEN) {
            return utils.truncateLabel((question.repeat ? '- ' : '')
                    + question.label, question.tag === 'hidden' ? ' (Hidden)' : '', MAXLEN);
        },
        truncateLabel: function (label, suffix, MAXLEN) {
            suffix = suffix || "";
            var MAXLEN = MAXLEN || 40,
                maxlen = MAXLEN - suffix.length;
            return ((label.length <= maxlen) ? (label) : (label.slice(0, maxlen) + "...")) + suffix;
        },
        truncateValue: function (value, MAXLEN) {
            MAXLEN = MAXLEN || 40;
            return (value.length <= MAXLEN) ? (value) : (value.slice(0, MAXLEN / 2) + "..." + value.slice(value.length - MAXLEN / 2));
        },
    };

    ko.bindingHandlers.questionsSelect = {
        /*
            The value used with this binding should be in the form:
            [
                {value: "someValue", label: "someLabel"},
                ...
            ]
         */
        init: function (element, valueAccessor, allBindingsAccessor) {
            var optionObjects = ko.utils.unwrapObservable(valueAccessor()),
                allBindings = ko.utils.unwrapObservable(allBindingsAccessor()),
                value = ko.utils.unwrapObservable(allBindings.value);

            // Add a warning if the current value isn't a legitimate question
            if (value && !_.some(optionObjects, function (option) {
                return option.value === value;
            })) {
                var option = {
                    label: gettext('Unidentified Question') + ' (' + value + ')',
                    value: value,
                };
                optionObjects = [option].concat(optionObjects);
                var $warning = $('<div class="help-block"></div>').text(gettext(
                    'We cannot find this question in the allowed questions for this field. ' +
                    'It is likely that you deleted or renamed the question. ' +
                    'Please choose a valid question from the dropdown.'
                ));
                $(element).after($warning);
                $(element).parent().addClass('has-error');
            }

            // Initialize select2
            var options = {
                    placeholder: gettext('Select a Question'),
                    dropdownCssClass: 'bigdrop',
                },
                data = _(optionObjects).map(function (o) {
                    return _.extend(o, {
                        id: o.value,
                        text: utils.getDisplay(o),
                    });
                }),
                templateSelection = function (o) {
                    if (!o.id) {
                        // This is the placeholder
                        return o.text;
                    }
                    return utils.getTruncatedDisplay(o);
                },
                templateResult = function (o) {
                    if (!o.value) {
                        // This is some select2 system option, like 'Searching...' text
                        return o.text;
                    }
                    return utils.getTruncatedDisplay(o, 90);
                };
            // Imperfect way to determine whether we're looking at select2 v3 or v4
            // v4 must use a <select>; v3 can but usually uses an <input>
            // Right now userreports are the only v3 usage of this binding, and they're all <input>
            if (element.nodeName.toLowerCase() === 'select') {
                options = _.extend(options, {
                    escapeMarkup: function (m) { return m; },
                    width: '100%',
                    data: [{id: '', text: ''}].concat(data),    // prepend option for placeholder
                    templateSelection: templateSelection,
                    templateResult: templateResult,
                });
            } else {
                options = _.extend(options, {
                    data: { results: data },
                    formatSelection: templateSelection,
                    formatResult: templateResult,
                });
            }
            $(element).select2(options);
            $(element).val(value).trigger('change.select2');
        },
        update: function (element, valueAccessor, allBindingsAccessor) {
            var optionObjects = ko.utils.unwrapObservable(valueAccessor()),
                allBindings = ko.utils.unwrapObservable(allBindingsAccessor()),
                value = ko.utils.unwrapObservable(allBindings.value),
                allowedValues = _.pluck(optionObjects, 'value'),
                $element = $(element),
                $container = $element.parent();

            if ($container.hasClass("has-error") && _.contains(allowedValues, value)) {
                // There was an error but it's fixed now, so remove the error and the bad option
                $container.removeClass("has-error");
                $container.find(".help-block").remove();
                _.each($element.find("option"), function (option) {
                    if (option.value && !_.contains(allowedValues, option.value)) {
                        $(option).remove();
                    }
                });
                $element.trigger('change.select2');
            }
        },
    };
}());

ko.bindingHandlers.casePropertyAutocomplete = {
    /*
     * Strip "attachment:" prefix and show icon for attachment properties.
     * Replace any spaces in free text with underscores.
     */
    init: function (element, valueAccessor) {
        $(element).on('textchange', function () {
            var $el = $(this);
            if ($el.val().match(/\s/)) {
                var pos = $el.caret('pos');
                $el.val($el.val().replace(/\s/g, '_'));
                $el.caret('pos', pos);
            }
        });
        ko.bindingHandlers.autocompleteAtwho.init(element, valueAccessor);
    },
    update: function (element, valueAccessor, allBindingsAccessor) {
        function wrappedValueAccessor() {
            return _.map(ko.unwrap(valueAccessor()), function (value) {
                if (value.indexOf("attachment:") === 0) {
                    var text = value.substring(11),
                        html = '<i class="fa fa-paperclip"></i> ' + text;
                    return {name: text, content: html};
                }
                return {name: value, content: value};
            });
        }
        ko.bindingHandlers.autocompleteAtwho.update(element, wrappedValueAccessor, allBindingsAccessor);
    },
};

// Originally from http://stackoverflow.com/a/17998880
ko.extenders.withPrevious = function (target) {
    // Define new properties for previous value and whether it's changed
    target.previous = ko.observable();

    // Subscribe to observable to update previous, before change.
    target.subscribe(function (v) {
        target.previous(v);
    }, null, 'beforeChange');

    // Return modified observable
    return target;
};

ko.bindingHandlers.numericValue = {
    init: function (element, valueAccessor, allBindingsAccessor) {
        var underlyingObservable = valueAccessor();
        var interceptor = ko.dependentObservable({
            read: underlyingObservable,
            write: function (value) {
                if ($.isNumeric(value)) {
                    underlyingObservable(parseFloat(value));
                } else if (value === '') {
                    underlyingObservable(null);
                }
            },
        });
        ko.bindingHandlers.value.init(element, function () { return interceptor; }, allBindingsAccessor);
    },
    update: ko.bindingHandlers.value.update,
};
