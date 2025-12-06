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

  // === Цвета интерфейса (стиль: черно-белый + зеленый акцент) ===
  const backgroundColor = "#000000";     // чисто чёрный фон
  const textColor = "#FFFFFF";           // белый текст
  const cardBackground = "#111111";      // карточка — мягкий чёрный
  const cardBorder = "1px solid #333";   // тонкая тёмно-серая граница
  const accentColor = "#4CAF50";         // зелёный акцент

  const isAdmin = user && user.id === ADMIN_ID;

  useEffect(() => {
    tg?.ready();
    tg?.expand();
  }, [tg]);

  const handleClick = (sectionId: string) => {
    tg?.sendData(
      JSON.stringify({
        type: "open_section",
        section: sectionId,
      })
    );
  };

  return (
    <div
      style={{
        padding: "20px",
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        background: backgroundColor,
        color: textColor,
        minHeight: "100vh",
      }}
    >
      {/* === Заголовок === */}
      <h1
        style={{
          textAlign: "center",
          fontSize: "24px",
          fontWeight: "700",
          color: textColor,
        }}
      >
        Thule Hub Russia
      </h1>

      {/* === Разделы === */}
      {SECTIONS.map((section) => (
        <div
          key={section.id}
          onClick={() => handleClick(section.id)}
          style={{
            padding: "18px",
            borderRadius: "16px",
            background: cardBackground,
            border: cardBorder,
            color: textColor,
            cursor: "pointer",
            boxShadow: "0 2px 8px rgba(0,0,0,0.4)",
            transition: "transform 0.12s ease, box-shadow 0.12s ease",
          }}
          onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.97)")}
          onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: "600",
              color: accentColor, // зелёный акцент в заголовке
            }}
          >
            {section.title}
          </div>

          <div
            style={{
              opacity: 0.8,
              fontSize: "13px",
              marginTop: "6px",
            }}
          >
            {section.description}
          </div>
        </div>
      ))}

      {/* === Админ-панель === */}
      {isAdmin && (
        <div
          onClick={() => handleClick("admin")}
          style={{
            padding: "18px",
            borderRadius: "16px",
            background: "#1a1a1a",
            border: "1px solid #444",
            cursor: "pointer",
            boxShadow: "0 2px 8px rgba(0,0,0,0.4)",
            transition: "transform 0.12s ease, box-shadow 0.12s ease",
          }}
          onMouseDown={(e) => (e.currentTarget.style.transform = "scale(0.97)")}
          onMouseUp={(e) => (e.currentTarget.style.transform = "scale(1)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <div
            style={{
              fontSize: "18px",
              fontWeight: "600",
              color: "#4CAF50",
            }}
          >
            ⚙️ Админ-панель
          </div>
          <div
            style={{
              opacity: 0.75,
              fontSize: "13px",
              marginTop: "6px",
              color: "#ccc",
            }}
          >
            Управление контентом и товарами
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
