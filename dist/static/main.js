// Carousel
(function() {
  var track = document.getElementById('carouselTrack');
  if (!track) return;

  var currentSlide = 0;
  var dots = document.querySelectorAll('#carouselDots span');
  var totalSlides = track.children.length;

  function updateCarousel() {
    track.style.transform = 'translateX(-' + (currentSlide * 100) + '%)';
    dots.forEach(function(d, i) { d.classList.toggle('active', i === currentSlide); });
  }

  window.nextSlide = function() {
    currentSlide = (currentSlide + 1) % totalSlides;
    updateCarousel();
  };

  window.prevSlide = function() {
    currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
    updateCarousel();
  };

  window.goToSlide = function(i) {
    currentSlide = i;
    updateCarousel();
  };

  var autoplay = setInterval(window.nextSlide, 5000);
  var carousel = document.getElementById('carousel');
  carousel.addEventListener('mouseenter', function() { clearInterval(autoplay); });
  carousel.addEventListener('mouseleave', function() { autoplay = setInterval(window.nextSlide, 5000); });
})();

// Mobile menu
function toggleMenu() {
  document.querySelector('.hamburger').classList.toggle('active');
  document.getElementById('mobileMenu').classList.toggle('open');
}
