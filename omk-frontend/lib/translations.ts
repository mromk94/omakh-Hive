/**
 * Multi-Language Translation System for OMK Hive
 * Supports: English, Spanish, Chinese, Japanese, Nigerian Pidgin, French, Russian, Arabic
 */

export type Language = 'en' | 'es' | 'zh' | 'ja' | 'pcm' | 'fr' | 'ru' | 'ar';

export interface Translations {
  nav: {
    dashboard: string;
    invest: string;
    portfolio: string;
    wallet: string;
    chat: string;
    learn: string;
  };
  landing: {
    subtitle: string;
    selectLanguage: string;
  };
  chat: {
    placeholder: string;
    send: string;
    typeMessage: string;
    connecting: string;
  };
  wallet: {
    connect: string;
    disconnect: string;
    connected: string;
    balance: string;
    address: string;
  };
  swap: {
    title: string;
    youPay: string;
    youReceive: string;
    balance: string;
    max: string;
    rate: string;
    fee: string;
    swap: string;
    connectFirst: string;
    enterAmount: string;
    insufficientBalance: string;
    swapping: string;
    success: string;
  };
  otc: {
    title: string;
    pricePerToken: string;
    minimumPurchase: string;
    startPurchase: string;
    connectWallet: string;
    enterWalletManually: string;
    howMuchOMK: string;
    totalCost: string;
    continue: string;
    contactInfo: string;
    fullName: string;
    email: string;
    review: string;
    submit: string;
    requestSubmitted: string;
    whatNext: string;
  };
  dashboard: {
    welcome: string;
    totalInvested: string;
    currentValue: string;
    totalReturn: string;
    myProperties: string;
    recentActivity: string;
  };
  common: {
    loading: string;
    error: string;
    tryAgain: string;
    close: string;
    back: string;
    next: string;
    confirm: string;
    cancel: string;
  };
}

export const translations: Record<Language, Translations> = {
  en: {
    nav: { dashboard: 'Dashboard', invest: 'Invest', portfolio: 'Portfolio', wallet: 'Wallet', chat: 'Chat', learn: 'Learn' },
    landing: { subtitle: 'Welcome to the Future of Finance', selectLanguage: 'Select your language' },
    chat: { placeholder: 'Ask me anything about OMK Hive...', send: 'Send', typeMessage: 'Type your message here', connecting: 'Connecting...' },
    wallet: { connect: 'Connect Wallet', disconnect: 'Disconnect', connected: 'Connected', balance: 'Balance', address: 'Address' },
    swap: { title: 'Token Swap', youPay: 'You Pay', youReceive: 'You Receive', balance: 'Balance', max: 'MAX', rate: 'Rate', fee: 'Fee', swap: 'Swap', connectFirst: 'Connect Wallet First', enterAmount: 'Enter Amount', insufficientBalance: 'Insufficient Balance', swapping: 'Swapping...', success: 'Success!' },
    otc: { title: 'OTC Token Purchase', pricePerToken: 'Price per OMK', minimumPurchase: 'Minimum Purchase', startPurchase: 'Start OTC Purchase Request', connectWallet: 'Connect Wallet', enterWalletManually: 'Enter Wallet Address Manually', howMuchOMK: 'How Much OMK?', totalCost: 'Total Cost (USD)', continue: 'Continue', contactInfo: 'Contact Information', fullName: 'Full Name', email: 'Email Address', review: 'Review Purchase', submit: 'Submit Request', requestSubmitted: 'Request Submitted!', whatNext: 'What Happens Next?' },
    dashboard: { welcome: 'Welcome back', totalInvested: 'Total Invested', currentValue: 'Current Value', totalReturn: 'Total Return', myProperties: 'My Properties', recentActivity: 'Recent Activity' },
    common: { loading: 'Loading...', error: 'Error', tryAgain: 'Try Again', close: 'Close', back: 'Back', next: 'Next', confirm: 'Confirm', cancel: 'Cancel' }
  },
  es: {
    nav: { dashboard: 'Panel', invest: 'Invertir', portfolio: 'Portafolio', wallet: 'Billetera', chat: 'Chat', learn: 'Aprender' },
    landing: { subtitle: 'Bienvenido al Futuro de las Finanzas', selectLanguage: 'Selecciona tu idioma' },
    chat: { placeholder: 'Pregúntame cualquier cosa sobre OMK Hive...', send: 'Enviar', typeMessage: 'Escribe tu mensaje aquí', connecting: 'Conectando...' },
    wallet: { connect: 'Conectar Billetera', disconnect: 'Desconectar', connected: 'Conectado', balance: 'Saldo', address: 'Dirección' },
    swap: { title: 'Intercambio de Tokens', youPay: 'Pagas', youReceive: 'Recibes', balance: 'Saldo', max: 'MÁX', rate: 'Tasa', fee: 'Comisión', swap: 'Intercambiar', connectFirst: 'Conectar Billetera Primero', enterAmount: 'Ingresar Cantidad', insufficientBalance: 'Saldo Insuficiente', swapping: 'Intercambiando...', success: '¡Éxito!' },
    otc: { title: 'Compra OTC de Tokens', pricePerToken: 'Precio por OMK', minimumPurchase: 'Compra Mínima', startPurchase: 'Iniciar Solicitud de Compra OTC', connectWallet: 'Conectar Billetera', enterWalletManually: 'Ingresar Dirección Manualmente', howMuchOMK: '¿Cuánto OMK?', totalCost: 'Costo Total (USD)', continue: 'Continuar', contactInfo: 'Información de Contacto', fullName: 'Nombre Completo', email: 'Correo Electrónico', review: 'Revisar Compra', submit: 'Enviar Solicitud', requestSubmitted: '¡Solicitud Enviada!', whatNext: '¿Qué Sigue?' },
    dashboard: { welcome: 'Bienvenido de nuevo', totalInvested: 'Total Invertido', currentValue: 'Valor Actual', totalReturn: 'Retorno Total', myProperties: 'Mis Propiedades', recentActivity: 'Actividad Reciente' },
    common: { loading: 'Cargando...', error: 'Error', tryAgain: 'Intentar de Nuevo', close: 'Cerrar', back: 'Atrás', next: 'Siguiente', confirm: 'Confirmar', cancel: 'Cancelar' }
  },
  zh: {
    nav: { dashboard: '仪表板', invest: '投资', portfolio: '投资组合', wallet: '钱包', chat: '聊天', learn: '学习' },
    landing: { subtitle: '欢迎来到金融的未来', selectLanguage: '选择您的语言' },
    chat: { placeholder: '询问关于 OMK Hive 的任何问题...', send: '发送', typeMessage: '在这里输入您的消息', connecting: '连接中...' },
    wallet: { connect: '连接钱包', disconnect: '断开连接', connected: '已连接', balance: '余额', address: '地址' },
    swap: { title: '代币交换', youPay: '您支付', youReceive: '您接收', balance: '余额', max: '最大', rate: '汇率', fee: '费用', swap: '交换', connectFirst: '请先连接钱包', enterAmount: '输入金额', insufficientBalance: '余额不足', swapping: '交换中...', success: '成功！' },
    otc: { title: 'OTC 代币购买', pricePerToken: '每 OMK 价格', minimumPurchase: '最小购买量', startPurchase: '开始 OTC 购买请求', connectWallet: '连接钱包', enterWalletManually: '手动输入钱包地址', howMuchOMK: '需要多少 OMK？', totalCost: '总费用 (USD)', continue: '继续', contactInfo: '联系信息', fullName: '全名', email: '电子邮件', review: '审核购买', submit: '提交请求', requestSubmitted: '请求已提交！', whatNext: '接下来会怎样？' },
    dashboard: { welcome: '欢迎回来', totalInvested: '总投资', currentValue: '当前价值', totalReturn: '总回报', myProperties: '我的资产', recentActivity: '最近活动' },
    common: { loading: '加载中...', error: '错误', tryAgain: '重试', close: '关闭', back: '返回', next: '下一步', confirm: '确认', cancel: '取消' }
  },
  ja: {
    nav: { dashboard: 'ダッシュボード', invest: '投資', portfolio: 'ポートフォリオ', wallet: 'ウォレット', chat: 'チャット', learn: '学ぶ' },
    landing: { subtitle: '金融の未来へようこそ', selectLanguage: '言語を選択' },
    chat: { placeholder: 'OMK Hiveについて何でも聞いてください...', send: '送信', typeMessage: 'ここにメッセージを入力', connecting: '接続中...' },
    wallet: { connect: 'ウォレット接続', disconnect: '切断', connected: '接続済み', balance: '残高', address: 'アドレス' },
    swap: { title: 'トークンスワップ', youPay: '支払い', youReceive: '受取', balance: '残高', max: '最大', rate: 'レート', fee: '手数料', swap: 'スワップ', connectFirst: '最初にウォレットを接続', enterAmount: '金額を入力', insufficientBalance: '残高不足', swapping: 'スワップ中...', success: '成功！' },
    otc: { title: 'OTCトークン購入', pricePerToken: 'OMKあたりの価格', minimumPurchase: '最小購入額', startPurchase: 'OTC購入リクエストを開始', connectWallet: 'ウォレット接続', enterWalletManually: 'ウォレットアドレスを手動入力', howMuchOMK: 'OMKはいくら？', totalCost: '合計費用 (USD)', continue: '続ける', contactInfo: '連絡先情報', fullName: '氏名', email: 'メールアドレス', review: '購入を確認', submit: 'リクエストを送信', requestSubmitted: 'リクエスト送信完了！', whatNext: '次のステップ？' },
    dashboard: { welcome: 'おかえりなさい', totalInvested: '総投資額', currentValue: '現在の価値', totalReturn: '総利益', myProperties: 'マイプロパティ', recentActivity: '最近のアクティビティ' },
    common: { loading: '読み込み中...', error: 'エラー', tryAgain: '再試行', close: '閉じる', back: '戻る', next: '次へ', confirm: '確認', cancel: 'キャンセル' }
  },
  pcm: {
    nav: { dashboard: 'Dashboard', invest: 'Invest', portfolio: 'Portfolio', wallet: 'Wallet', chat: 'Chat', learn: 'Learn' },
    landing: { subtitle: 'Welcome to di Future of Finance', selectLanguage: 'Pick your language' },
    chat: { placeholder: 'Ask me anytin about OMK Hive...', send: 'Send', typeMessage: 'Type your message for here', connecting: 'Connecting...' },
    wallet: { connect: 'Connect Wallet', disconnect: 'Disconnect', connected: 'Connected', balance: 'Balance', address: 'Address' },
    swap: { title: 'Token Swap', youPay: 'You go Pay', youReceive: 'You go Receive', balance: 'Balance', max: 'MAX', rate: 'Rate', fee: 'Fee', swap: 'Swap', connectFirst: 'Connect Wallet First', enterAmount: 'Enter Amount', insufficientBalance: 'Money no dey', swapping: 'Swapping...', success: 'E don work!' },
    otc: { title: 'OTC Token Purchase', pricePerToken: 'Price per OMK', minimumPurchase: 'Minimum Purchase', startPurchase: 'Start OTC Purchase', connectWallet: 'Connect Wallet', enterWalletManually: 'Enter Wallet Address Manually', howMuchOMK: 'How much OMK you wan buy?', totalCost: 'Total Cost (USD)', continue: 'Continue', contactInfo: 'Contact Info', fullName: 'Full Name', email: 'Email', review: 'Review Purchase', submit: 'Submit Request', requestSubmitted: 'Request don submit!', whatNext: 'Wetin go happen next?' },
    dashboard: { welcome: 'Welcome back', totalInvested: 'Total Invested', currentValue: 'Current Value', totalReturn: 'Total Return', myProperties: 'My Properties', recentActivity: 'Recent Activity' },
    common: { loading: 'Loading...', error: 'Error', tryAgain: 'Try Again', close: 'Close', back: 'Back', next: 'Next', confirm: 'Confirm', cancel: 'Cancel' }
  },
  fr: {
    nav: { dashboard: 'Tableau de Bord', invest: 'Investir', portfolio: 'Portefeuille', wallet: 'Portefeuille', chat: 'Discuter', learn: 'Apprendre' },
    landing: { subtitle: 'Bienvenue dans le Futur de la Finance', selectLanguage: 'Sélectionnez votre langue' },
    chat: { placeholder: 'Posez-moi des questions sur OMK Hive...', send: 'Envoyer', typeMessage: 'Tapez votre message ici', connecting: 'Connexion...' },
    wallet: { connect: 'Connecter le Portefeuille', disconnect: 'Déconnecter', connected: 'Connecté', balance: 'Solde', address: 'Adresse' },
    swap: { title: 'Échange de Tokens', youPay: 'Vous Payez', youReceive: 'Vous Recevez', balance: 'Solde', max: 'MAX', rate: 'Taux', fee: 'Frais', swap: 'Échanger', connectFirst: 'Connecter d\'abord le Portefeuille', enterAmount: 'Entrer le Montant', insufficientBalance: 'Solde Insuffisant', swapping: 'Échange en cours...', success: 'Succès!' },
    otc: { title: 'Achat OTC de Tokens', pricePerToken: 'Prix par OMK', minimumPurchase: 'Achat Minimum', startPurchase: 'Démarrer l\'Achat OTC', connectWallet: 'Connecter le Portefeuille', enterWalletManually: 'Entrer l\'Adresse Manuellement', howMuchOMK: 'Combien d\'OMK?', totalCost: 'Coût Total (USD)', continue: 'Continuer', contactInfo: 'Informations de Contact', fullName: 'Nom Complet', email: 'Adresse Email', review: 'Réviser l\'Achat', submit: 'Soumettre la Demande', requestSubmitted: 'Demande Soumise!', whatNext: 'Que se Passe-t-il Ensuite?' },
    dashboard: { welcome: 'Bon Retour', totalInvested: 'Total Investi', currentValue: 'Valeur Actuelle', totalReturn: 'Rendement Total', myProperties: 'Mes Propriétés', recentActivity: 'Activité Récente' },
    common: { loading: 'Chargement...', error: 'Erreur', tryAgain: 'Réessayer', close: 'Fermer', back: 'Retour', next: 'Suivant', confirm: 'Confirmer', cancel: 'Annuler' }
  },
  ru: {
    nav: { dashboard: 'Панель', invest: 'Инвестировать', portfolio: 'Портфолио', wallet: 'Кошелёк', chat: 'Чат', learn: 'Обучение' },
    landing: { subtitle: 'Добро пожаловать в Будущее Финансов', selectLanguage: 'Выберите язык' },
    chat: { placeholder: 'Спросите меня о OMK Hive...', send: 'Отправить', typeMessage: 'Введите сообщение здесь', connecting: 'Подключение...' },
    wallet: { connect: 'Подключить Кошелёк', disconnect: 'Отключить', connected: 'Подключено', balance: 'Баланс', address: 'Адрес' },
    swap: { title: 'Обмен Токенов', youPay: 'Вы Платите', youReceive: 'Вы Получаете', balance: 'Баланс', max: 'МАКС', rate: 'Курс', fee: 'Комиссия', swap: 'Обменять', connectFirst: 'Сначала Подключите Кошелёк', enterAmount: 'Введите Сумму', insufficientBalance: 'Недостаточно Средств', swapping: 'Обмен...', success: 'Успешно!' },
    otc: { title: 'OTC Покупка Токенов', pricePerToken: 'Цена за OMK', minimumPurchase: 'Минимальная Покупка', startPurchase: 'Начать OTC Покупку', connectWallet: 'Подключить Кошелёк', enterWalletManually: 'Ввести Адрес Вручную', howMuchOMK: 'Сколько OMK?', totalCost: 'Общая Стоимость (USD)', continue: 'Продолжить', contactInfo: 'Контактная Информация', fullName: 'Полное Имя', email: 'Электронная Почта', review: 'Проверить Покупку', submit: 'Отправить Запрос', requestSubmitted: 'Запрос Отправлен!', whatNext: 'Что Дальше?' },
    dashboard: { welcome: 'С Возвращением', totalInvested: 'Всего Инвестировано', currentValue: 'Текущая Стоимость', totalReturn: 'Общая Прибыль', myProperties: 'Мои Объекты', recentActivity: 'Недавняя Активность' },
    common: { loading: 'Загрузка...', error: 'Ошибка', tryAgain: 'Повторить', close: 'Закрыть', back: 'Назад', next: 'Далее', confirm: 'Подтвердить', cancel: 'Отмена' }
  },
  ar: {
    nav: { dashboard: 'لوحة التحكم', invest: 'استثمار', portfolio: 'المحفظة', wallet: 'المحفظة', chat: 'دردشة', learn: 'تعلم' },
    landing: { subtitle: 'مرحباً بك في مستقبل التمويل', selectLanguage: 'اختر لغتك' },
    chat: { placeholder: 'اسألني أي شيء عن OMK Hive...', send: 'إرسال', typeMessage: 'اكتب رسالتك هنا', connecting: 'جاري الاتصال...' },
    wallet: { connect: 'ربط المحفظة', disconnect: 'قطع الاتصال', connected: 'متصل', balance: 'الرصيد', address: 'العنوان' },
    swap: { title: 'مبادلة الرموز', youPay: 'تدفع', youReceive: 'تستلم', balance: 'الرصيد', max: 'الحد الأقصى', rate: 'السعر', fee: 'الرسوم', swap: 'مبادلة', connectFirst: 'قم بتوصيل المحفظة أولاً', enterAmount: 'أدخل المبلغ', insufficientBalance: 'رصيد غير كافٍ', swapping: 'جاري المبادلة...', success: 'نجح!' },
    otc: { title: 'شراء رموز OTC', pricePerToken: 'السعر لكل OMK', minimumPurchase: 'الحد الأدنى للشراء', startPurchase: 'ابدأ طلب شراء OTC', connectWallet: 'ربط المحفظة', enterWalletManually: 'أدخل عنوان المحفظة يدوياً', howMuchOMK: 'كم OMK؟', totalCost: 'التكلفة الإجمالية (USD)', continue: 'متابعة', contactInfo: 'معلومات الاتصال', fullName: 'الاسم الكامل', email: 'البريد الإلكتروني', review: 'مراجعة الشراء', submit: 'إرسال الطلب', requestSubmitted: 'تم إرسال الطلب!', whatNext: 'ما الذي سيحدث بعد ذلك?' },
    dashboard: { welcome: 'مرحباً بعودتك', totalInvested: 'إجمالي الاستثمار', currentValue: 'القيمة الحالية', totalReturn: 'العائد الإجمالي', myProperties: 'ممتلكاتي', recentActivity: 'النشاط الأخير' },
    common: { loading: 'جاري التحميل...', error: 'خطأ', tryAgain: 'حاول مرة أخرى', close: 'إغلاق', back: 'رجوع', next: 'التالي', confirm: 'تأكيد', cancel: 'إلغاء' }
  }
};

// Hook to get translations
export function useTranslations(language: Language = 'en'): Translations {
  return translations[language] || translations.en;
}
