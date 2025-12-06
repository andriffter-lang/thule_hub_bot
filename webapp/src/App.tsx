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
    tg?.sendData(
      JSON.stringify({
        type: "open_section",
        section: sectionId,
      })
    );
  };

  return (
    <div style={{
      padding: "20px",
      display: "flex",
      flexDirection: "column",
      gap: "12px"
    }}>
      <h1 style={{ textAlign: "center", color: "black" }}>Thule Hub Mini App</h1>

      {SECTIONS.map(section => (
        <div
          key={section.id}
          onClick={() => handleClick(section.id)}
          style={{
            padding: "16px",
            borderRadius: "12px",
            border: "1px solid rgba(0,0,0,0.1)",
            background: "black",
            cursor: "pointer",
          }}
        >
          <div style={{ fontSize: "18px", fontWeight: "bold" }}>
            {section.title}
          </div>
          <div style={{ opacity: 0.7, fontSize: "14px", marginTop: "4px" }}>
            {section.description}
          </div>
        </div>
      ))}

      {isAdmin && (
        <div
          onClick={() => handleClick("admin")}
          style={{
            padding: "16px",
            borderRadius: "12px",
            border: "1px solid rgba(0,0,0,0.1)",
            background: "#fffbe6",
            cursor: "pointer",
          }}
        >
          <div style={{ fontSize: "18px", fontWeight: "bold" }}>
            ⚙️ Админ-панель
          </div>
          <div style={{ opacity: 0.7, fontSize: "14px", marginTop: "4px" }}>
            Управление контентом и товарами
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
