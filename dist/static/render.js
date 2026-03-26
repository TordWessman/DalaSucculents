// Rendering functions — replaces Jinja2 template logic
var DalaRender = (function() {

  function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function formatPrice(value) {
    return '$' + Number(value).toFixed(2);
  }

  function renderProductCard(product) {
    var soldOutBtn = product.sold_out
      ? '<span class="btn-sold-out">Sold Out</span>'
      : '<span class="btn-shop">Shop</span>';
    return '<a href="product.html?slug=' + encodeURIComponent(product.slug) + '" class="product-card">'
      + '<img src="' + escapeHtml(product.image_url) + '" alt="' + escapeHtml(product.name) + '" loading="lazy">'
      + '<div class="product-info">'
      + '<div class="product-name">' + escapeHtml(product.name) + '</div>'
      + '<div class="product-scientific">' + escapeHtml(product.scientific_name) + '</div>'
      + '<div class="product-bottom">'
      + '<span class="product-price">' + formatPrice(product.price) + '</span>'
      + soldOutBtn
      + '</div></div></a>';
  }

  function renderCarousel(slides, trackEl, dotsEl) {
    var trackHtml = '';
    var dotsHtml = '';
    for (var i = 0; i < slides.length; i++) {
      var s = slides[i];
      trackHtml += '<div class="carousel-slide">'
        + '<img src="' + escapeHtml(s.image_url) + '" alt="' + escapeHtml(s.heading) + '">'
        + '<div class="carousel-overlay"><div class="carousel-text">'
        + '<h2>' + escapeHtml(s.heading) + '</h2>'
        + '<p>' + escapeHtml(s.subheading) + '</p>'
        + '<a class="carousel-btn" href="' + escapeHtml(s.button_link) + '">' + escapeHtml(s.button_text) + '</a>'
        + '</div></div></div>';
      dotsHtml += '<span' + (i === 0 ? ' class="active"' : '') + ' onclick="goToSlide(' + i + ')"></span>';
    }
    trackEl.innerHTML = trackHtml;
    dotsEl.innerHTML = dotsHtml;
  }

  function renderProductDetail(product, containerEl) {
    var soldOutBtn = product.sold_out
      ? '<span class="btn-sold-out">Sold Out</span>'
      : '<span class="btn-shop">Add to Cart</span>';
    containerEl.innerHTML =
      '<div class="product-detail">'
      + '<div class="product-detail-image">'
      + '<img src="' + escapeHtml(product.image_url_large) + '" alt="' + escapeHtml(product.name) + '">'
      + '</div>'
      + '<div class="product-detail-info">'
      + '<h1>' + escapeHtml(product.name) + '</h1>'
      + '<div class="product-scientific">' + escapeHtml(product.scientific_name) + '</div>'
      + '<span class="product-price">' + formatPrice(product.price) + '</span>'
      + '<div class="description">' + escapeHtml(product.description) + '</div>'
      + soldOutBtn
      + '</div></div>';
  }

  return {
    escapeHtml: escapeHtml,
    formatPrice: formatPrice,
    renderProductCard: renderProductCard,
    renderCarousel: renderCarousel,
    renderProductDetail: renderProductDetail
  };
})();
