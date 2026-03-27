export default function SpecimenList({ specimens }) {
  if (!specimens || specimens.length === 0) return null;

  return (
    <div className="specimen-list">
      <h3>Specimens</h3>
      <div className="specimen-grid">
        {specimens.map(sp => (
          <div key={sp.id} className="specimen-item">
            {sp.image_url && (
              <img src={sp.image_url} alt={sp.specimen_code} className="specimen-image" />
            )}
            <div className="specimen-info">
              <span className="specimen-code">{sp.specimen_code}</span>
              {sp.propagation_method && (
                <span className="specimen-prop">
                  {sp.propagation_method}
                  {sp.propagation_date && ` (${sp.propagation_date})`}
                </span>
              )}
              {sp.for_sale && sp.price != null && (
                <span className="specimen-price">${Number(sp.price).toFixed(2)}</span>
              )}
              {sp.for_sale ? (
                <span className="specimen-available">Available</span>
              ) : (
                <span className="specimen-collection">Collection only</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
