var lastQuery = '';
var selectedTerm = '';
var selectedRelation = '';

// These relations should be derived directly from the OWL store, but
// then the owlkb doesn't really use those URLs so...

var relations = [
    "topObjectProperty (ANY)",
    "part-of (RICORDO)",
    "has-part (RICORDO)",
    "contained-in (RICORDO)",
    "has_participant (RICORDO)",
    "inheres-in (RICORDO)",
    "participates-in (RICORDO)",
    "results_in (RICORDO)",
    "results_in_movement_of (RICORDO)",
    "results_in_transport_from (RICORDO)",
    "results_in_transport_to (RICORDO)",
    "inheres_in_part_of (RICORDO)",
    "occurs_in (RICORDO)",
    "composed_of (OPB)",
    "physicalPropertyOf (OPB)",
    "contained_in (RO)",
    "part_of (RO)",
    "attaches_to (FMA)",
    "bounds (FMA)",
    "branch_of (FMA)",
    "constitutional_part_of (FMA)",
    "regional_part_of (FMA)",
    "systemic_part_of (FMA)",
    "has_part (GO)",
    "negatively_regulates (GO)",
    "positively_regulates (GO)",
    "regulates (GO)",
    "OBO_REL_part_of (PATO)",
    "decreased_in_magnitude_relative_to (PATO)",
    "different_in_magnitude_relative_to (PATO)",
    "directly_associated_with (PATO)",
    "has_cross_section (PATO)",
    "has_dividend_entity (PATO)",
    "has_dividend_quality (PATO)",
    "has_divisor_entity (PATO)",
    "has_divisor_quality (PATO)",
    "has_part (PATO)",
    "has_ratio_quality (PATO)",
    "has_relative_magnitude (PATO)",
    "increased_in_magnitude_relative_to (PATO)",
    "inheres_in (PATO)",
    "inversely_associated_with (PATO)",
    "is_magnitude_of (PATO)",
    "is_measurement_of (PATO)",
    "is_unit_of (PATO)",
    "reciprocal_of (PATO)",
    "similar_in_magnitude_relative_to (PATO)",
    "singly_occurring_form_of (PATO)",
    "towards (PATO)",
    "part_of (PATO)"
];

var max_terms = 32;
var last_values = {};
var something;

function untag(selector, key) {
    if (last_values[selector] != $(selector).val()) {
        div = $(key);
        div.html('');
        last_values[selector] = $(selector).val();
    }
}

$(document).ready(function () {

    $(".queryrelation").typeahead({
        source: relations,
        items: 16,
        updater: updateRelationSelection,
        minLength: 2
    });

    hookOwlInput(
        ".queryterm",
        window.location.href.toString().replace(
            /pmr2_ricordo\/query.*/, 'pmr2_ricordo/owlterms/'),
        updateTermSelection
    );

    hookOwlInput(
        "#form-widgets-simple_query",
        window.location.href.toString().replace(
            /pmr2_ricordo\/query.*/, 'pmr2_ricordo/owlterms/'),
        updateSimpleTermSelection
    );

    $("#form-widgets-simple_query").keyup(function() {
        untag("#form-widgets-simple_query", '#valid_term')
    });
    $("#form-widgets-simple_query").change(function() {
        untag("#form-widgets-simple_query", '#valid_term')
    });

    $('#btnBuildQuery').button().on('click', function() {
        var result = '';
        if (selectedRelation) {
            result = selectedRelation + 'some ';
        }
        result = result + selectedTerm;
        $('#form-widgets-query').val(result);
    });

});

function hookOwlInput(selector, target_base, updater) {
    var label_url_map = {};
    updaterValueAdded = function(item) {
        value = label_url_map[item];
        console.log(value);
        return updater(item, value);
    };

    $(selector).typeahead({
        source: suggestTerms(selector, target_base, label_url_map),
        matcher: function(term) { return true; },
        updater: updaterValueAdded,
        items: max_terms,
        minLength: 2
    });

    // disable browser autocomplete
    $(selector).attr('autocomplete', 'off');
}

function suggestTerms(selector, target_base, label_url_map) {
    suggestion = function(query, process) {
        setTimeout(function() {
            if ((query == $(selector).val()) && (query != lastQuery)) {
                lastQuery = query;
                getTerms(target_base, query, process, label_url_map);
            }
        }, 200);
    };
    return suggestion;
}

function getTerms(target_base, query, process, label_url_map) {
    target = target_base + query + '/' + max_terms;
    console.log(target);
    $.getJSON(target, function(data) {
        var items = [];
        $.each(data["results"], function(key, val) {
            value = val[0] + ' (' + val[1].replace(/[^#]*#/, '') + ')';
            items.push(value);
            label_url_map[value] = val[1];
        })
        process(items);
    });
}

function updateTermSelection(item, value) {
    selectedTerm = item.replace(/[^(]*\((.*)\)/, '$1');
    return item;
}


function updateRelationSelection(item) {
    selectedRelation = item.replace(/([^(]*).*/, '$1');
    return item;
}

function updateSimpleTermSelection(item, value) {
    selectedTerm = item.replace(/[^(]*\((.*)\)/, '$1');
    var selectedText = item.replace(/(.*) \(.*\)/, '$1');
    var target_parent = "#form-widgets-simple_query";
    var key = "valid_term";
    var div = $('#' + key);

    if (div.length == 0) {
        // create the element
        $(target_parent).parent().append(
            '<span id="' + key + '"></span>');
        div = $('#' + key);
    }
    div.html('<span style="color:#070;font-size:133%;">✔</span>(' +
        selectedTerm + ')');

    target_input = $('#form-widgets-term_id').val(selectedTerm);

    // ensure the change/keyup events don't reset the thing..
    last_values[target_parent] = selectedText;
    return selectedText;
}
