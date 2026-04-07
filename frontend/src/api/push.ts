import { apiClient } from './client'

export async function getVapidKey(): Promise<string> {
  const { data } = await apiClient.get<{ public_key: string }>('/api/v1/push/vapid-key')
  return data.public_key
}

export async function subscribePush(subscription: PushSubscription): Promise<void> {
  const json = subscription.toJSON()
  await apiClient.post('/api/v1/push/subscribe', {
    endpoint: json.endpoint,
    keys: {
      p256dh: json.keys?.p256dh,
      auth: json.keys?.auth,
    },
  })
}

export async function unsubscribePush(endpoint: string): Promise<void> {
  await apiClient.delete('/api/v1/push/subscribe', {
    data: { endpoint },
  })
}

export async function getTestMode(): Promise<boolean> {
  const { data } = await apiClient.get<{ test_mode: boolean }>('/api/v1/push/test-mode')
  return data.test_mode
}

export async function sendTestPush(): Promise<{ status: string; delay_seconds: number }> {
  const { data } = await apiClient.post('/api/v1/push/test')
  return data
}
