// DalaDB — vanilla JS data layer (D1-style API client)
var DalaDB = (function() {
  var BASE = '/api';

  function fetchJSON(url) {
    return fetch(BASE + url).then(function(res) {
      if (!res.ok) throw new Error('API error: ' + res.status);
      return res.json();
    });
  }

  return {
    getProducts: function() {
      return fetchJSON('/products').then(function(data) { return data.results; });
    },
    getProduct: function(slug) {
      return fetchJSON('/products/' + encodeURIComponent(slug)).then(function(data) { return data.result; });
    },
    getCarouselSlides: function() {
      return fetchJSON('/carousel').then(function(data) { return data.results; });
    }
  };
})();
