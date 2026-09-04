'use client'

interface RecommendationCardProps {
  title: string
  description: string
  imageUrl: string
  onClick: () => void
}

export function RecommendationCard({
  title,
  description,
  imageUrl,
  onClick,
}: RecommendationCardProps) {
  return (
    <div
      onClick={onClick}
      className="group cursor-pointer glass rounded-2xl p-4 transition-all duration-300 border-2 shadow-xl hover:shadow-2xl hover:-translate-y-2 transform"
      style={{ borderColor: 'var(--glass-border)' }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--spotify-green)';
        e.currentTarget.style.boxShadow = '0 0 30px rgba(29, 185, 84, 0.4)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--glass-border)';
        e.currentTarget.style.boxShadow = '';
      }}
    >
      <div className="aspect-square rounded-xl overflow-hidden mb-4 shadow-lg" style={{
        background: `linear-gradient(135deg, var(--bright-green), var(--bright-yellow), var(--bright-blue), var(--spotify-green))`
      }}>
        {imageUrl && (
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          />
        )}
      </div>
      <h4 className="font-bold text-sm mb-1 truncate" style={{ color: 'var(--text-bright)' }}>
        {title}
      </h4>
      <p className="text-xs truncate font-medium" style={{ color: 'var(--text-dim)' }}>{description}</p>
    </div>
  )
}
