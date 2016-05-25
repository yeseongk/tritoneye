Rails.application.routes.draw do
  resources :floors
  resources :parking_lots

  root "floors#index"
end
