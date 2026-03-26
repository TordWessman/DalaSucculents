import { useState, useEffect, useRef } from 'react';

export default function Carousel({ slides }) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const carouselRef = useRef(null);
  const autoplayRef = useRef(null);

  const totalSlides = slides.length;

  function nextSlide() {
    setCurrentSlide(prev => (prev + 1) % totalSlides);
  }

  function prevSlide() {
    setCurrentSlide(prev => (prev - 1 + totalSlides) % totalSlides);
  }

  function goToSlide(i) {
    setCurrentSlide(i);
  }

  function startAutoplay() {
    autoplayRef.current = setInterval(nextSlide, 5000);
  }

  function stopAutoplay() {
    clearInterval(autoplayRef.current);
  }

  useEffect(() => {
    startAutoplay();
    return () => stopAutoplay();
  }, [totalSlides]);

  if (!slides || slides.length === 0) return null;

  return (
    <section
      className="carousel"
      id="carousel"
      ref={carouselRef}
      onMouseEnter={stopAutoplay}
      onMouseLeave={startAutoplay}
    >
      <div
        className="carousel-track"
        style={{ transform: `translateX(-${currentSlide * 100}%)` }}
      >
        {slides.map((slide, i) => (
          <div className="carousel-slide" key={i}>
            <img src={slide.image_url} alt={slide.heading} />
            <div className="carousel-overlay">
              <div className="carousel-text">
                <h2>{slide.heading}</h2>
                <p>{slide.subheading}</p>
                <a className="carousel-btn" href={slide.button_link}>{slide.button_text}</a>
              </div>
            </div>
          </div>
        ))}
      </div>
      <div className="carousel-dots">
        {slides.map((_, i) => (
          <span
            key={i}
            className={i === currentSlide ? 'active' : ''}
            onClick={() => goToSlide(i)}
          />
        ))}
      </div>
      <div className="carousel-nav">
        <button onClick={prevSlide} aria-label="Previous">&larr;</button>
        <button onClick={nextSlide} aria-label="Next">&rarr;</button>
      </div>
    </section>
  );
}
