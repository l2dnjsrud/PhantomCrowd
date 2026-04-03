import { createI18n } from 'vue-i18n'
import en from './en'
import ko from './ko'

const savedLocale = localStorage.getItem('phantomcrowd-locale') || 'en'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'en',
  messages: { en, ko },
})

export function setLocale(locale: string) {
  ;(i18n.global.locale as any).value = locale
  localStorage.setItem('phantomcrowd-locale', locale)
}

export function getLocale(): string {
  return (i18n.global.locale as any).value
}

export default i18n
