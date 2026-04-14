import { ref, type Ref } from 'vue'
import { useRouter, type RouteLocationRaw } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { getErrorMessage } from '@/types/errors'
import { isDemoMode } from '@/stores/auth'

export interface FormSubmitConfig<TPayload> {
  store: {
    create: (data: TPayload) => Promise<unknown>
    update: (id: number, data: TPayload) => Promise<unknown>
    remove?: (id: number) => Promise<void>
  }
  buildPayload: () => TPayload
  validate?: () => string | null
  successRoute: string | RouteLocationRaw
  entityLabel: string
  isEdit: Ref<boolean>
  editId?: Ref<number | undefined>
}

export function useFormSubmit<TPayload>(config: FormSubmitConfig<TPayload>) {
  const router = useRouter()
  const toast = useToast()
  const confirm = useConfirm()
  const submitting = ref(false)
  const error = ref<string | null>(null)

  async function handleSubmit() {
    error.value = null

    if (config.validate) {
      const validationError = config.validate()
      if (validationError) {
        error.value = validationError
        return
      }
    }

    submitting.value = true
    try {
      const payload = config.buildPayload()

      if (config.isEdit.value && config.editId?.value) {
        await config.store.update(config.editId.value, payload)
      } else {
        await config.store.create(payload)
      }

      if (isDemoMode.value) {
        toast.add({
          severity: 'info',
          summary: config.entityLabel,
          detail: 'Збережено в демо-режимі (тимчасово)',
          life: 3000,
        })
      } else {
        toast.add({
          severity: 'success',
          summary: config.entityLabel,
          detail: config.isEdit.value
            ? `${config.entityLabel} оновлено`
            : `${config.entityLabel} створено`,
          life: 3000,
        })
      }

      router.push(config.successRoute)
    } catch (e: unknown) {
      error.value = getErrorMessage(
        e,
        config.isEdit.value ? 'Помилка оновлення' : 'Помилка створення',
      )
    } finally {
      submitting.value = false
    }
  }

  async function handleDelete() {
    if (!config.store.remove || !config.editId?.value) return

    const id = config.editId.value
    confirm.require({
      message: `Видалити ${config.entityLabel.toLowerCase()}?`,
      header: 'Підтвердження',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Видалити',
      rejectLabel: 'Скасувати',
      accept: async () => {
        try {
          await config.store.remove!(id)

          if (isDemoMode.value) {
            toast.add({
              severity: 'info',
              summary: config.entityLabel,
              detail: 'Видалено в демо-режимі (тимчасово)',
              life: 3000,
            })
          } else {
            toast.add({
              severity: 'success',
              summary: config.entityLabel,
              detail: `${config.entityLabel} видалено`,
              life: 3000,
            })
          }

          router.push(config.successRoute)
        } catch (e: unknown) {
          error.value = getErrorMessage(e, 'Помилка видалення')
        }
      },
    })
  }

  return {
    submitting,
    error,
    handleSubmit,
    handleDelete,
  }
}
