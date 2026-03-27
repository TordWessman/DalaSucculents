/**
 * Format a plant's botanical name with proper italicization segments.
 * Returns an array of { text, italic } objects for rendering.
 *
 * Rules:
 *   - Genus and species are always italic
 *   - Infraspecific rank abbreviations (subsp., var., f.) are roman
 *   - Infraspecific epithets are italic
 *   - Cultivar names are roman, wrapped in single quotes
 *   - Author citation is roman
 */
export function formatBotanicalName(plant) {
  const parts = [];

  // Genus + species (italic)
  parts.push({ text: plant.genus + ' ' + plant.species, italic: true });

  if (plant.display_name) {
    // Detect infraspecific parts from display_name
    const dn = plant.display_name;
    const base = plant.genus + ' ' + plant.species;

    if (dn.includes(' subsp. ')) {
      const epithet = dn.split(' subsp. ')[1];
      parts.push({ text: ' subsp. ', italic: false });
      parts.push({ text: epithet, italic: true });
    } else if (dn.includes(' var. ')) {
      const epithet = dn.split(' var. ')[1];
      parts.push({ text: ' var. ', italic: false });
      parts.push({ text: epithet, italic: true });
    } else if (dn.includes(' f. ')) {
      const epithet = dn.split(' f. ')[1];
      parts.push({ text: ' f. ', italic: false });
      parts.push({ text: epithet, italic: true });
    } else if (dn.includes("'")) {
      // Cultivar: 'Name'
      const match = dn.match(/'([^']+)'/);
      if (match) {
        parts.push({ text: " '" + match[1] + "'", italic: false });
      }
    }
  }

  // Author citation (roman)
  if (plant.author_citation) {
    parts.push({ text: ' ' + plant.author_citation, italic: false });
  }

  return parts;
}
