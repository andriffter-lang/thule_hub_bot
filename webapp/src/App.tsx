import { useEffect } from "react";

const SECTIONS = [
  { id: "shop", title: "🏪 Магазин", description: "Купить оборудование Thule" },
  { id: "rental", title: "🚗 Аренда", description: "Арендовать бокс или багажник" },
  { id: "market", title: "📦 Рынок", description: "Продать или купить б/у оборудование" },
  { id: "repair", title: "🧰 Ремонт", description: "Заявка на ремонт оборудования" },
  { id: "faq", title: "❓ FAQ", description: "Ответы на частые вопросы" },
  { id: "community", title: "💬 Сообщество", description: "Обсуждение и чат" },
];

const ADMIN_ID = 230325201;

function App() {
  const tg = window.Telegram?.WebApp;
  const user = tg?.initDataUnsafe?.user;

  const isAdmin = user && user.id === ADMIN_ID;

  useEffect(() => {
    tg?.ready();
    tg?.expand();
  }, [tg]);

  const handleClick = (sectionId: string) => {
    tg?.sendData(JSON.stringify({ type: "open_section", section: sectionId }));
  };

  return (
    <div
      style={{
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        minHeight: "100vh",
        color: "#fff",
        background: "transparent",        
      }}
    >
      <h1
        style={{
          textAlign: "center",
          fontSize: "26px",
          fontWeight: "700",
          marginBottom: "10px",
          color: "#4CAF50",
          textShadow: "0 3px 6px rgba(0,0,0,0.6)",
        }}
      >
        Thule Hub Russia
      </h1>

      {SECTIONS.map((section, index) => (
        <div
          key={section.id}
          onClick={() => handleClick(section.id)}
          style={{
            padding: "18px",
            borderRadius: "14px",
            background: "#3d3d3d",
            backgroundImage: `
              repeating-linear-gradient(
                45deg,
                rgba(0,0,0,0.15) 0,
                rgba(0,0,0,0.15) 2px,
                rgba(255,255,255,0.05) 2px,
                rgba(255,255,255,0.05) 4px
              )
            `,
            border: "1px solid #222",
            boxShadow: "0 6px 14px rgba(0,0,0,0.5)",
            cursor: "pointer",

            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            textAlign: "center",

            opacity: 0,
            transform: "translateY(-40px)",
            animation: `drop 0.6s ease forwards`,
            animationDelay: `${index * 0.12}s`,
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: "600",
              color: "#4CAF50",
              marginBottom: "4px",
              textShadow: "0 2px 4px rgba(0,0,0,0.5)",
            }}
          >
            {section.title}
          </div>

          <div
            style={{
              opacity: 0.8,
              fontSize: "13px",
            }}
          >
            {section.description}
          </div>
        </div>
      ))}

      {isAdmin && (
        <div
          onClick={() => handleClick("admin")}
          style={{
            padding: "18px",
            borderRadius: "14px",
            background: "#444",
            border: "1px solid #333",
            cursor: "pointer",
            boxShadow: "0 6px 14px rgba(0,0,0,0.55)",
            textAlign: "center",
            opacity: 0,
            transform: "translateY(-40px)",
            animation: `drop 0.6s ease forwards`,
            animationDelay: `${SECTIONS.length * 0.12}s`,
          }}
        >
          <div style={{ fontSize: "20px", fontWeight: "600", color: "#4CAF50" }}>
            ⚙️ Админ-панель
          </div>

          <div style={{ opacity: 0.75, fontSize: "13px" }}>
            Управление контентом и товарами
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
