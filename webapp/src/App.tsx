import { useEffect } from "react";

function App() {
  const tg = window.Telegram?.WebApp;
  const user = tg?.initDataUnsafe?.user;

  useEffect(() => {
    tg?.ready();
    tg?.expand();
  }, []);

  const sendToBot = () => {
    const payload = {
      action: "hello_from_miniapp",
      user: user,
    };

    tg?.sendData(JSON.stringify(payload));
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Thule Hub Mini App</h1>

      {user && (
        <div>
          <p>Привет, {user.first_name}!</p>
          <p>ID: {user.id}</p>
        </div>
      )}

      <button
        style={{ padding: 10, marginTop: 10 }}
        onClick={sendToBot}
      >
        Отправить данные боту
      </button>
    </div>
  );
}

export default App;
