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

  // random rotation / tile shift for unique concrete tiles
  const randomize = () => {
    const rot = Math.floor(Math.random() * 6 - 3); // -3° to +3°
    const offsetX = Math.floor(Math.random() * 8 - 4); // -4px to +4px
    const offsetY = Math.floor(Math.random() * 8 - 4);

    return {
      transform: `translate(${offsetX}px, ${offsetY}px) rotate(${rot}deg)`,
    };
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
          textShadow: "0 3px 6px rgba(0,0,0,0.7)",
        }}
      >
        Thule Hub Russia
      </h1>

      {/* MAIN BUTTONS */}
      {SECTIONS.map((section, index) => {
        const rand = randomize();

        return (
          <div
            key={section.id}
            onClick={() => handleClick(section.id)}
            style={{
              padding: "20px",
              borderRadius: "10px",

              backgroundImage: `
                url('/images/concrete_base.jpg'),
                url('/images/concrete_cracks.png'),
                url('/images/concrete_noise.png')
              `,
              backgroundBlendMode: "overlay, normal, soft-light",
              backgroundSize: "cover, cover, 300%",
              backgroundPosition: "center, center, center",

              border: "2px solid #3a3a3a",
              boxShadow: "0 8px 20px rgba(0,0,0,0.75)",

              cursor: "pointer",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",

              opacity: 0,
              transform: "translateY(-40px)",
              animation: `drop 0.65s cubic-bezier(.25,.75,.45,1.4) forwards`,
              animationDelay: `${index * 0.13}s`,

              // random rotation/offset for realism
              ...rand,
            }}
            onMouseDown={(e) =>
              (e.currentTarget.style.transform = "scale(0.97)")
            }
            onMouseUp={(e) =>
              (e.currentTarget.style.transform = "scale(1)")
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.transform = "scale(1)")
            }
          >
            <div
              style={{
                fontSize: "20px",
                fontWeight: "700",
                color: "#ffffff",
                textShadow: "0 2px 5px rgba(0,0,0,0.7)",
              }}
            >
              {section.title}
            </div>

            <div
              style={{
                opacity: 0.85,
                fontSize: "13px",
                color: "#e5e5e5",
                textShadow: "0 1px 3px rgba(0,0,0,0.6)",
                marginTop: "6px",
              }}
            >
              {section.description}
            </div>
          </div>
        );
      })}

      {/* ADMIN PANEL */}
      {isAdmin && (
        <div
          onClick={() => handleClick("admin")}
          style={{
            padding: "20px",
            borderRadius: "10px",

            backgroundImage: `
              url('/images/concrete_base.jpg'),
              url('/images/concrete_cracks.png'),
              url('/images/concrete_noise.png')
            `,
            backgroundBlendMode: "overlay, normal, soft-light",
            backgroundSize: "cover, cover, 300%",
            backgroundPosition: "center",

            border: "2px solid #3a3a3a",
            boxShadow: "0 8px 20px rgba(0,0,0,0.75)",

            cursor: "pointer",
            textAlign: "center",

            opacity: 0,
            transform: "translateY(-40px)",
            animation: `drop 0.65s cubic-bezier(.25,.75,.45,1.4) forwards`,
            animationDelay: `${SECTIONS.length * 0.13}s`,
          }}
        >
          <div
            style={{
              fontSize: "20px",
              fontWeight: "700",
              color: "#4CAF50",
              textShadow: "0 2px 5px rgba(0,0,0,0.7)",
            }}
          >
            ⚙️ Админ-панель
          </div>
          <div
            style={{
              opacity: 0.8,
              fontSize: "13px",
              color: "#e5e5e5",
              marginTop: "6px",
              textShadow: "0 1px 3px rgba(0,0,0,0.6)",
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
