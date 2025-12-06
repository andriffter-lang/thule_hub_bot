export {};

declare global {
  interface TelegramWebAppUser {
    id: number;
    first_name?: string;
    last_name?: string;
    username?: string;
  }

  interface TelegramWebApp {
    initData: string;
    initDataUnsafe: {
      user?: TelegramWebAppUser;
      [key: string]: any;
    };
    ready: () => void;
    expand: () => void;
    close: () => void;
    sendData: (data: string) => void;
    MainButton: {
      text: string;
      isVisible: boolean;
      show: () => void;
      hide: () => void;
      onClick: (cb: () => void) => void;
    };
  }

  interface TelegramNamespace {
    WebApp: TelegramWebApp;
  }

  interface Window {
    Telegram: TelegramNamespace;
  }
}
