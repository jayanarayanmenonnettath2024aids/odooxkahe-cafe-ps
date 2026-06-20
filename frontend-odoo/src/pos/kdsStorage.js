const STORAGE_KEY = 'brewnest-kds-tickets'

const SEED_TICKETS = [
  {
    id: '2201',
    items: [
      { name: 'Masala Tea', qty: 3, category: 'Quick Bites', prepared: false },
      { name: 'Lassi', qty: 2, category: 'Quick Bites', prepared: false },
    ],
    manuallyCompleted: false,
    createdAt: Date.now() - 8 * 60000,
  },
  {
    id: '2202',
    items: [
      { name: 'Coffee', qty: 2, category: 'Drink', prepared: false },
      { name: 'Water', qty: 1, category: 'Drink', prepared: false },
    ],
    manuallyCompleted: false,
    createdAt: Date.now() - 7 * 60000,
  },
  {
    id: '2203',
    items: [
      { name: 'Burger', qty: 2, category: 'Quick Bites', prepared: false },
      { name: 'Water', qty: 2, category: 'Drink', prepared: true },
    ],
    manuallyCompleted: false,
    createdAt: Date.now() - 6 * 60000,
  },
  {
    id: '2204',
    items: [
      { name: 'Masala Tea', qty: 3, category: 'Quick Bites', prepared: true },
      { name: 'Lassi', qty: 3, category: 'Quick Bites', prepared: true },
      { name: 'Coffee', qty: 1, category: 'Drink', prepared: false },
    ],
    manuallyCompleted: false,
    createdAt: Date.now() - 5 * 60000,
  },
  {
    id: '2205',
    items: [
      { name: 'Masala Tea', qty: 3, category: 'Quick Bites', prepared: false },
      { name: 'Lassi', qty: 3, category: 'Quick Bites', prepared: false },
      { name: 'Coffee', qty: 3, category: 'Drink', prepared: false },
      { name: 'Water', qty: 3, category: 'Drink', prepared: true },
    ],
    manuallyCompleted: false,
    createdAt: Date.now() - 4 * 60000,
  },
  {
    id: '2206',
    items: [
      { name: 'Pizza', qty: 1, category: 'Desert', prepared: true },
      { name: 'Coffee', qty: 1, category: 'Drink', prepared: true },
    ],
    manuallyCompleted: false,
    createdAt: Date.now() - 3 * 60000,
  },
  {
    id: '2207',
    items: [
      { name: 'Burger', qty: 1, category: 'Quick Bites', prepared: false },
    ],
    manuallyCompleted: true,
    createdAt: Date.now() - 2 * 60000,
  },
]

export function loadTickets() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(SEED_TICKETS))
      return SEED_TICKETS
    }
    return JSON.parse(raw)
  } catch {
    return SEED_TICKETS
  }
}

export function saveTickets(tickets) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tickets))
}

export function upsertTicket(orderId, items) {
  const tickets = loadTickets()
  const ticket = {
    id: orderId,
    items: items.map((item) => ({
      name: item.name,
      qty: item.qty,
      category: item.category || '',
      prepared: false,
    })),
    manuallyCompleted: false,
    createdAt: Date.now(),
  }
  const existingIndex = tickets.findIndex((t) => t.id === orderId)
  const next = existingIndex >= 0
    ? tickets.map((t, i) => (i === existingIndex ? ticket : t))
    : [...tickets, ticket]
  saveTickets(next)
}

export function ticketStage(ticket) {
  const allPrepared = ticket.items.every((i) => i.prepared)
  if (ticket.manuallyCompleted || allPrepared) return 'completed'
  if (ticket.items.some((i) => i.prepared)) return 'preparing'
  return 'to-cook'
}

export const KDS_STORAGE_KEY = STORAGE_KEY
