
$( function() {
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


$( "#id_manifestations_searchable" ).catcomplete({
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

$( "#id_subjects" ).autocomplete({
  source: subjects_autocomplete,
  minLength: 0,
  appendTo: '#query-fieldset'
});

$( "#id_original_catalogue" ).autocomplete({
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

// Search all values on select
$( "#id_original_catalogue" ).on("click", function()    {
    $(this).autocomplete('search', '');
});

$( "#id_manifestations_searchable" ).on("click", function()    {
    $(this).catcomplete('search', '');
});

$( "#id_subjects" ).on("click", function()    {
    $(this).autocomplete('search', '');
});

} );