(function(){
  'use strict';

  function autosizeSelect(select){
    if (!select) return;
    try {
      var mirrorId = select.id ? (select.id + '__mirror') : '';
      var mirror = mirrorId ? document.getElementById(mirrorId) : null;
      if(!mirror){
        mirror = document.createElement('span');
        if (mirrorId) mirror.id = mirrorId;
        mirror.className = 'select-mirror';
        // Place mirror next to the select to inherit fonts properly
        (select.parentNode || document.body).appendChild(mirror);
      }
      var cs = window.getComputedStyle(select);
      var padding = (parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight)) || 0;
      var border = (parseFloat(cs.borderLeftWidth) + parseFloat(cs.borderRightWidth)) || 0;
      mirror.style.font = cs.font;
      mirror.style.fontSize = cs.fontSize;
      mirror.style.fontFamily = cs.fontFamily;
      mirror.style.letterSpacing = cs.letterSpacing;
      mirror.style.textTransform = cs.textTransform;
      var text = '';
      if (select.options && select.selectedIndex >= 0) {
        text = select.options[select.selectedIndex].text;
      }
      mirror.textContent = text;
      var arrowExtra = 24; // extra space for native select arrow
      select.style.width = (mirror.offsetWidth + padding + border + arrowExtra) + 'px';
    } catch (e) {
      // fail silently
    }
  }

  function initAutosizeOnElement(select){
    if (!select) return;
    var handler = function(){ autosizeSelect(select); };
    autosizeSelect(select); // initial
    select.addEventListener('change', handler);
    // Also fire on mutation of options (e.g., dynamic content)
    var mo; try {
      mo = new MutationObserver(handler);
      mo.observe(select, { childList: true, subtree: true, characterData: true });
    } catch(_) {}
    window.addEventListener('resize', handler);
  }

  function init(){
    // Explicit known field
    var sortSel = document.getElementById('id_sort_by');
    if (sortSel) initAutosizeOnElement(sortSel);

    // Generic hook: any select with data-autosize-select
    var list = document.querySelectorAll('select[data-autosize-select]');
    for (var i=0; i<list.length; i++) initAutosizeOnElement(list[i]);
  }

  // Run ASAP
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
