interface FeatureCardProps {
  icon: string
  title: string
  description: string
  delay?: string
}

const FeatureCard = ({ icon, title, description, delay = '0s' }: FeatureCardProps) => {
  return (
    <div
      className="feature-card animate-float"
      style={{ animationDelay: delay }}
    >
      <div className="text-5xl mb-4">{icon}</div>
      <h3 className="text-2xl font-bold mb-3 gradient-text">{title}</h3>
      <p className="text-slate-300 leading-relaxed">{description}</p>
    </div>
  )
}

export default FeatureCard

