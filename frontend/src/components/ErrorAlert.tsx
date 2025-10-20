interface ErrorAlertProps {
  message: string;
  severity?: 'error' | 'warning';
  dismissible?: boolean;
  onDismiss?: () => void;
}

export default function ErrorAlert({
  message,
  severity = 'error',
  dismissible = false,
  onDismiss
}: ErrorAlertProps) {
  const isError = severity === 'error';
  const bgColor = isError ? 'bg-red-50' : 'bg-yellow-50';
  const borderColor = isError ? 'border-red-500' : 'border-yellow-500';
  const textColor = isError ? 'text-red-800' : 'text-yellow-800';
  const messageColor = isError ? 'text-red-700' : 'text-yellow-700';
  const icon = isError ? '❌' : '⚠️';

  return (
    <div className={`${bgColor} border-l-4 ${borderColor} p-4 rounded-r-lg`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start">
          <span className="text-2xl mr-3">{icon}</span>
          <div>
            <p className={`font-semibold ${textColor}`}>
              {isError ? 'Error Loading Data' : 'Warning'}
            </p>
            <p className={`${messageColor} text-sm mt-1`}>{message}</p>
            <p className={`${messageColor} text-xs mt-2 opacity-75`}>
              Please check your AWS credentials and network connection.
            </p>
          </div>
        </div>
        {dismissible && (
          <button
            onClick={onDismiss}
            className={`ml-4 ${textColor} hover:opacity-75 transition-opacity`}
            aria-label="Dismiss alert"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}