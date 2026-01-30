
/**
 * Simulates a SHA-256 hash for a given string.
 * Real forensic tools would use standard crypto libraries on binary data.
 */
export const generateMockHash = (content: string): string => {
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    const char = content.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  const result = Math.abs(hash).toString(16).padStart(64, '0');
  return `sha256:${result}`;
};

export const formatTimestamp = (dateString: string): string => {
  return new Date(dateString).toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

export const getEvidenceIcon = (type: string) => {
  switch (type) {
    case 'IMAGE': return '🖼️';
    case 'VIDEO': return '📽️';
    case 'AUDIO': return '🎙️';
    case 'DOCUMENT': return '📄';
    case 'TEXT': return '📝';
    default: return '📁';
  }
};
