const FIELDS = [
  { key: 'vegetation_period', label: 'Vegetation Period', tooltip: 'The season when the plant actively grows' },
  { key: 'substrate', label: 'Substrate', tooltip: 'Recommended growing medium or soil mix' },
  { key: 'winter_temp_range', label: 'Winter Temperature', tooltip: 'Minimum temperature range during dormancy' },
  { key: 'watering', label: 'Watering', tooltip: 'Watering needs during the growing season' },
  { key: 'exposure', label: 'Exposure', tooltip: 'Light requirements (full sun, partial shade, etc.)' },
];

export default function CultivationTable({ cultivation }) {
  if (!cultivation) return null;

  const hasData = FIELDS.some(f => cultivation[f.key]);
  if (!hasData) return null;

  return (
    <table className="cultivation-table">
      <tbody>
        {FIELDS.map(({ key, label, tooltip }) => {
          const value = cultivation[key];
          if (!value) return null;
          return (
            <tr key={key}>
              <th>
                <span className="cultivation-label" title={tooltip}>
                  {label}
                </span>
              </th>
              <td>{value}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
