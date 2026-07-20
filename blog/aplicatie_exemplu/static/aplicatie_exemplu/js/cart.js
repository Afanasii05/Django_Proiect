/**
 * Cart Management System - Amigurumi World
 * Uses localStorage for persistence and data-attributes for safe product data.
 */

const Cart = {
  // ─── Storage ───────────────────────────────────────────────
  getCart: function () {
    try {
      const cart = localStorage.getItem("shoppingCart");
      return cart ? JSON.parse(cart) : [];
    } catch (e) {
      console.error("Eroare la citirea coșului:", e);
      return [];
    }
  },

  saveCart: function (cart) {
    localStorage.setItem("shoppingCart", JSON.stringify(cart));
    this.updateCartBadge();
  },

  // ─── Add / Remove / Update ─────────────────────────────────
  addToCart: function (product, quantity) {
    quantity = quantity || 1;
    let cart = this.getCart();
    const existing = cart.find(function (item) {
      return item.id === product.id;
    });

    if (existing) {
      existing.quantity += quantity;
    } else {
      cart.push({
        id: product.id,
        nume: product.nume,
        pret: parseFloat(product.pret),
        poza: product.poza || "",
        quantity: quantity,
      });
    }

    this.saveCart(cart);
    this.showNotification(
      '"' + product.nume + '" a fost adăugat în coș! (' + quantity + "x)"
    );
  },

  removeFromCart: function (productId) {
    let cart = this.getCart();
    cart = cart.filter(function (item) {
      return item.id !== productId;
    });
    this.saveCart(cart);
    this.renderCartPage();
  },

  updateQuantity: function (productId, change) {
    let cart = this.getCart();
    const product = cart.find(function (item) {
      return item.id === productId;
    });

    if (product) {
      product.quantity += change;
      if (product.quantity <= 0) {
        cart = cart.filter(function (item) {
          return item.id !== productId;
        });
      }
    }

    this.saveCart(cart);
    this.renderCartPage();
  },

  clearCart: function () {
    localStorage.removeItem("shoppingCart");
    this.updateCartBadge();
    this.renderCartPage();
  },

  // ─── Computed ──────────────────────────────────────────────
  getCartTotal: function () {
    return this.getCart().reduce(function (total, item) {
      return total + item.pret * item.quantity;
    }, 0);
  },

  getCartCount: function () {
    return this.getCart().reduce(function (count, item) {
      return count + item.quantity;
    }, 0);
  },

  // ─── Badge ─────────────────────────────────────────────────
  updateCartBadge: function () {
    var badge = document.getElementById("cart-badge");
    if (badge) {
      var count = this.getCartCount();
      badge.textContent = count;
      badge.style.display = count > 0 ? "inline-flex" : "none";
    }
  },

  // ─── Notification ──────────────────────────────────────────
  showNotification: function (message) {
    // Remove any existing notification
    var old = document.querySelector(".cart-notification");
    if (old) old.remove();

    var notification = document.createElement("div");
    notification.className = "cart-notification";
    notification.innerHTML =
      '<span class="notif-icon">✓</span> <span>' + message + "</span>";

    notification.style.cssText =
      "position:fixed;top:20px;right:20px;" +
      "background:linear-gradient(135deg,#4CAF50,#45a049);color:#fff;" +
      "padding:14px 24px;border-radius:12px;z-index:10000;" +
      "box-shadow:0 8px 32px rgba(0,0,0,0.18);" +
      "display:flex;align-items:center;gap:10px;" +
      "font-family:'Nunito',sans-serif;font-weight:600;font-size:0.95rem;" +
      "animation:cartSlideIn 0.4s cubic-bezier(.22,.68,0,1.1);";

    document.body.appendChild(notification);

    setTimeout(function () {
      notification.style.animation = "cartSlideOut 0.35s ease forwards";
      setTimeout(function () {
        notification.remove();
      }, 350);
    }, 2500);
  },

  // ─── Cart Page Render ──────────────────────────────────────
  renderCartPage: function () {
    var container = document.getElementById("cart-content");
    if (!container) return;

    var cart = this.getCart();

    if (cart.length === 0) {
      container.innerHTML =
        '<div class="cart-empty">' +
        '<div class="empty-icon">🛒</div>' +
        "<h2>Coșul tău este gol</h2>" +
        "<p>Nu ai adăugat încă niciun produs în coș.</p>" +
        '<a href="/produs/" class="btn btn-primary">Descoperă Produsele</a>' +
        "</div>";
      return;
    }

    // Payment notice
    var html =
      '<div class="cart-notice">' +
      '<span class="notice-icon">ℹ️</span>' +
      '<div class="notice-text">' +
      '<strong>Notă importantă:</strong> Plata nu se efectuează online acum. Comanda va fi finalizată și detaliile de plată vor fi stabilite după ce veți fi contactat pe Instagram.' +
      '</div>' +
      '</div>';

    html +=
      '<table class="cart-table">' +
      "<thead><tr>" +
      "<th>Produs</th><th>Preț unitar</th><th>Cantitate</th><th>Subtotal</th><th></th>" +
      "</tr></thead><tbody>";

    var self = this;
    cart.forEach(function (item) {
      var subtotal = (item.pret * item.quantity).toFixed(2);
      var imgHtml = item.poza
        ? '<img src="' +
          item.poza +
          '" alt="' +
          item.nume +
          '" class="product-image">'
        : '<div class="product-image-placeholder">📦</div>';

      html +=
        '<tr class="cart-item" data-item-id="' +
        item.id +
        '">' +
        '<td class="product-info">' +
        imgHtml +
        '<span class="product-name">' +
        item.nume +
        "</span></td>" +
        '<td class="product-price">' +
        item.pret.toFixed(2) +
        " RON</td>" +
        '<td class="product-quantity">' +
        '<button class="qty-btn minus" data-qty-change="' +
        item.id +
        '" data-dir="-1">−</button>' +
        '<span class="qty-value">' +
        item.quantity +
        "</span>" +
        '<button class="qty-btn plus" data-qty-change="' +
        item.id +
        '" data-dir="1">+</button></td>' +
        '<td class="product-subtotal">' +
        subtotal +
        " RON</td>" +
        '<td class="product-remove">' +
        '<button class="remove-btn" data-remove-item="' +
        item.id +
        '">🗑️</button></td>' +
        "</tr>";
    });

    html += "</tbody></table>";

    // Summary section
    var total = this.getCartTotal();
    var livrareGratuita = total >= 200;
    var costLivrare = livrareGratuita ? 0 : 15;
    var totalFinal = total + costLivrare;

    html +=
      '<div class="cart-summary">' +
      '<div class="summary-row"><span>Subtotal produse:</span><span>' +
      total.toFixed(2) +
      " RON</span></div>" +
      '<div class="summary-row"><span>Livrare:</span><span>' +
      (livrareGratuita
        ? '<span class="free-shipping">GRATUITĂ ✓</span>'
        : costLivrare.toFixed(2) + " RON") +
      "</span></div>";

    if (!livrareGratuita) {
      var remaining = (200 - total).toFixed(2);
      html +=
        '<div class="shipping-hint">Mai adaugă ' +
        remaining +
        " RON pentru livrare gratuită!</div>";
    }

    html +=
      '<div class="cart-total">' +
      '<span class="total-label">Total de plată:</span>' +
      '<span class="total-value">' +
      totalFinal.toFixed(2) +
      " RON</span></div>";

    // Instagram and Location Form Inputs
    html +=
      '<div class="checkout-form">' +
      '<h3>Detalii Contact & Livrare</h3>' +
      '<div class="form-group">' +
      '<label for="instagram-input">Nume cont Instagram <span class="required">*</span></label>' +
      '<input type="text" id="instagram-input" class="form-input" placeholder="ex: @nume_utilizator" required>' +
      '</div>' +
      '<div class="form-group">' +
      '<label for="locatie-input">Locație / Adresă Completă <span class="required">*</span></label>' +
      '<textarea id="locatie-input" class="form-input" placeholder="Oraș, Județ, Adresă completă de livrare" rows="2" required></textarea>' +
      '</div>' +
      '<div id="checkout-error" class="checkout-error-msg" style="display:none;"></div>' +
      '</div>';

    html +=
      '<div class="cart-actions">' +
      '<button class="btn btn-secondary" id="clear-cart-btn">Golește Coșul</button>' +
      '<a href="/produs/" class="btn btn-outline">Continuă Cumpărăturile</a>' +
      '<button class="btn btn-success" id="checkout-btn">Finalizează Comanda</button>' +
      "</div></div>";

    container.innerHTML = html;

    // Bind events on rendered elements
    this._bindCartEvents();
  },

  renderSuccessPage: function (instagram) {
    var container = document.getElementById("cart-content");
    if (!container) return;

    container.innerHTML =
      '<div class="cart-success">' +
      '<div class="success-icon">🎉</div>' +
      "<h2>Comandă Trimisă cu Succes!</h2>" +
      "<p>Detaliile coșului tău au fost trimise prin e-mail.</p>" +
      '<p class="contact-notice">Te vom contacta în curând pe contul de Instagram <strong>' + instagram + '</strong> pentru stabilirea detaliilor de plată și livrare.</p>' +
      '<a href="/produs/" class="btn btn-primary" style="margin-top: 1.5rem;">Înapoi la Produse</a>' +
      "</div>";
  },

  _bindCartEvents: function () {
    var self = this;

    // Clear cart
    var clearBtn = document.getElementById("clear-cart-btn");
    if (clearBtn) {
      clearBtn.addEventListener("click", function () {
        self.clearCart();
      });
    }

    // Quantity change buttons
    var qtyBtns = document.querySelectorAll("[data-qty-change]");
    qtyBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = parseInt(btn.getAttribute("data-qty-change"));
        var dir = parseInt(btn.getAttribute("data-dir"));
        self.updateQuantity(id, dir);
      });
    });

    // Remove buttons
    var removeBtns = document.querySelectorAll("[data-remove-item]");
    removeBtns.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = parseInt(btn.getAttribute("data-remove-item"));
        self.removeFromCart(id);
      });
    });

    // Checkout/Finalizează comanda submit
    var checkoutBtn = document.getElementById("checkout-btn");
    if (checkoutBtn) {
      checkoutBtn.addEventListener("click", function (e) {
        e.preventDefault();
        
        var instagramInput = document.getElementById("instagram-input");
        var locatieInput = document.getElementById("locatie-input");
        var errorDiv = document.getElementById("checkout-error");
        
        var instagram = instagramInput ? instagramInput.value.trim() : "";
        var locatie = locatieInput ? locatieInput.value.trim() : "";
        
        if (!instagram || !locatie) {
          if (errorDiv) {
            errorDiv.textContent = "Vă rugăm să completați atât numele contului de Instagram, cât și locația.";
            errorDiv.style.display = "block";
          }
          return;
        }
        
        if (errorDiv) {
          errorDiv.style.display = "none";
        }
        
        // Disable checkout button to prevent double submit
        checkoutBtn.disabled = true;
        checkoutBtn.textContent = "Se trimite comanda...";
        
        var cartData = self.getCart();
        var csrfToken = "";
        var cartContainer = document.querySelector(".cart-container");
        if (cartContainer) {
          csrfToken = cartContainer.getAttribute("data-csrf") || "";
        }
        
        fetch("/trimite_comanda/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
          },
          body: JSON.stringify({
            instagram: instagram,
            locatie: locatie,
            cart: cartData
          })
        })
        .then(function (response) {
          return response.json();
        })
        .then(function (res) {
          if (res.success) {
            // Clear cart from storage and update badge without calling full renderCartPage (which would show empty cart)
            localStorage.removeItem("shoppingCart");
            self.updateCartBadge();
            self.renderSuccessPage(instagram);
          } else {
            checkoutBtn.disabled = false;
            checkoutBtn.textContent = "Finalizează Comanda";
            if (errorDiv) {
              errorDiv.textContent = res.error || "A apărut o eroare la trimiterea comenzii. Încercați din nou.";
              errorDiv.style.display = "block";
            }
          }
        })
        .catch(function (err) {
          checkoutBtn.disabled = false;
          checkoutBtn.textContent = "Finalizează Comanda";
          if (errorDiv) {
            errorDiv.textContent = "Eroare de rețea. Vă rugăm să verificați conexiunea la internet.";
            errorDiv.style.display = "block";
          }
          console.error("Error submitting order:", err);
        });
      });
    }
  },
};

// ─── Initialization ────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", function () {
  Cart.updateCartBadge();

  // Render cart page if on cart route
  if (document.getElementById("cart-content")) {
    Cart.renderCartPage();
  }

  // Event delegation: listen for clicks on [data-add-to-cart] buttons
  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-add-to-cart]");
    if (!btn) return;

    e.preventDefault();

    var product = {
      id: parseInt(btn.getAttribute("data-id")),
      nume: btn.getAttribute("data-nume"),
      pret: btn.getAttribute("data-pret"),
      poza: btn.getAttribute("data-poza") || "",
    };

    // Check for a quantity input on the page (detail page)
    var qtyInput = document.getElementById("qty-input");
    var quantity = qtyInput ? parseInt(qtyInput.value) || 1 : 1;

    Cart.addToCart(product, quantity);

    // Button animation feedback
    var originalText = btn.textContent;
    btn.textContent = "✓ Adăugat!";
    btn.classList.add("btn-added");
    setTimeout(function () {
      btn.textContent = originalText;
      btn.classList.remove("btn-added");
    }, 1200);
  });
});

// ─── CSS Animations (injected once) ────────────────────────────
(function () {
  var style = document.createElement("style");
  style.textContent =
    "@keyframes cartSlideIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}" +
    "@keyframes cartSlideOut{from{transform:translateX(0);opacity:1}to{transform:translateX(120%);opacity:0}}" +
    "@keyframes cartFadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}" +
    ".cart-item{animation:cartFadeIn 0.3s ease both}" +
    ".btn-added{background:#4CAF50 !important;transform:scale(1.05);transition:all 0.2s ease}";
  document.head.appendChild(style);
})();
