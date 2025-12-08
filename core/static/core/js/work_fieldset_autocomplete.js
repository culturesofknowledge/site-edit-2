
$( function() {
// Clean up any previously created ARIA live regions from jQuery UI that may have accumulated
try {
  $("div.ui-helper-hidden-accessible[role='status']").remove();
} catch(e) {}
$.widget( "custom.catcomplete", $.ui.autocomplete, {
  _create: function() {
    this._super();
    this.widget().menu( "option", "items", "> :not(.ui-autocomplete-category)" );
  },
  _renderMenu: function( ul, items ) {
    var that = this,
      currentCategory = "";
    $.each( items, function( index, item ) {
      var li;
      if ( item.category != currentCategory ) {
        ul.append( "<li class='ui-autocomplete-category'>" + item.category + "</li>" );
        currentCategory = item.category;
      }
      li = that._renderItemData( ul, item );
      if ( item.category ) {
        li.attr( "aria-label", item.category + " : " + item.label );
      }
    });
  }
});


var $manif = $( "#id_manifestations_searchable" );
if ( $manif.length && !$manif.data("ui-autocomplete") ) {
  $manif.catcomplete({
    delay: 0,
    source: function( request, response ) {
      var matcher = new RegExp( $.ui.autocomplete.escapeRegex( request.term ), "i" );
      response( $.grep( manif_autocomplete, function( value ) {
        value = value.label || value.value || value;
        return matcher.test( value ) || matcher.test( normalize( value ) );
      }) );
    },
    minLength: 0,
    appendTo: '#query-fieldset'
  });
}

var $subjects = $( "#id_subjects" );
if ( $subjects.length && !$subjects.data("ui-autocomplete") ) {
  $subjects.autocomplete({
    source: subjects_autocomplete,
    minLength: 0,
    appendTo: '#query-fieldset'
  });
}

var $catalog = $( "#id_original_catalogue" );
if ( $catalog.length && !$catalog.data("ui-autocomplete") ) {
  $catalog.autocomplete({
    source: function( request, response ) {
      var matcher = new RegExp( $.ui.autocomplete.escapeRegex( request.term ), "i" );
      response( $.grep( catalogs_autocomplete, function( value ) {
        value = value.label || value.value || value;
        return matcher.test( value ) || matcher.test( normalize( value ) );
      }) );
    },
    minLength: 0,
    appendTo: '#query-fieldset'
  });
}

// Search all values on select (ensure single binding)
$catalog.off('click.autocompleteAll').on("click.autocompleteAll", function() {
  $(this).autocomplete('search', '');
});

$manif.off('click.autocompleteAll').on("click.autocompleteAll", function() {
  $(this).catcomplete('search', '');
});

$subjects.off('click.autocompleteAll').on("click.autocompleteAll", function() {
  $(this).autocomplete('search', '');
});

} );