export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_active: boolean;
}

export interface Address {
  id: string;
  label: string;
  full_name: string;
  phone: string;
  address_line1: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
}
