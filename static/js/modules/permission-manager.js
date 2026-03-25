// Módulo de Gestión de Permisos/Roles
window.PermissionManager = {
    // Estado local del módulo
    state: {
        available: [],
        assigned: [],
        search: {
            available: '',
            assigned: ''
        },
        selectedIds: {
            available: new Set(),
            assigned: new Set()
        }
    },

    // Método de inicialización
    init(data = {}) {
        // Reiniciar estado para que cada apertura del modal sea consistente.
        const hasOwn = (obj, prop) => Object.prototype.hasOwnProperty.call(obj, prop);

        if (hasOwn(data, 'available')) this.state.available = data.available || [];
        if (hasOwn(data, 'assigned')) this.state.assigned = data.assigned || [];

        this.state.search.available = '';
        this.state.search.assigned = '';
        this.state.selectedIds.available.clear();
        this.state.selectedIds.assigned.clear();

        // Solo inicializar si existe el formulario
        const form = document.getElementById('grupo-form');
        if (!form) return;

        this.setupEventListeners();
        this.renderLists();
    },

    // Configurar event listeners
    setupEventListeners() {
        // Inputs de búsqueda
        document.querySelectorAll('.search-input').forEach(input => {
            input.addEventListener('input', (e) => this.handleSearch(e));
        });

        // Botones de movimiento
        const btnRight = document.getElementById('btn-move-right');
        const btnLeft = document.getElementById('btn-move-left');

        if (btnRight) {
            btnRight.addEventListener('click', () => this.moveItems('available', 'assigned'));
        }

        if (btnLeft) {
            btnLeft.addEventListener('click', () => this.moveItems('assigned', 'available'));
        }

        // Formulario
        const form = document.getElementById('grupo-form');
        if (form) {
            form.addEventListener('submit', () => this.updateHiddenInput());
        }
    },

    // Manejar búsqueda
    handleSearch(e) {
        const listKey = e.target.dataset.list;
        this.state.search[listKey] = e.target.value;
        this.renderList(listKey);
    },

    // Renderizar una lista específica
    renderList(listKey) {
        const container = document.querySelector(`[data-list-container="${listKey}"]`);
        if (!container) return;

        const searchTerm = this.state.search[listKey].toLowerCase();
        const items = this.state[listKey].filter(p =>
            p.name.toLowerCase().includes(searchTerm)
        );

        container.innerHTML = '';

        if (items.length === 0) {
            container.innerHTML = '<div class="p-4 text-center text-gray-400 text-xs italic">No hay elementos</div>';
            return;
        }

        items.forEach(perm => {
            const div = document.createElement('div');
            div.classList.add('permission-item', 'px-4', 'py-2', 'cursor-pointer', 'text-sm', 'transition-colors', 'duration-150', 'border-b', 'border-gray-200');

            if (this.state.selectedIds[listKey].has(perm.id)) {
                div.classList.add('selected');
            }

            div.textContent = perm.name;
            div.addEventListener('click', () => this.toggleItem(perm.id, listKey));
            container.appendChild(div);
        });
    },

    // Renderizar ambas listas
    renderLists() {
        this.renderList('available');
        this.renderList('assigned');
    },

    // Alternar selección de item
    toggleItem(id, listKey) {
        if (this.state.selectedIds[listKey].has(id)) {
            this.state.selectedIds[listKey].delete(id);
        } else {
            this.state.selectedIds[listKey].add(id);
        }
        this.renderList(listKey);
        this.updateButtonStates();
    },

    // Mover items entre listas
    moveItems(from, to) {
        if (this.state.selectedIds[from].size === 0) return;

        const selected = Array.from(this.state.selectedIds[from]);

        selected.forEach(id => {
            const item = this.state[from].find(p => p.id === id);
            if (item) {
                this.state[to].push(item);
                this.state[from] = this.state[from].filter(p => p.id !== id);
            }
        });

        this.state.selectedIds[from].clear();
        this.state.selectedIds[to].clear();

        this.renderLists();
        this.updateButtonStates();
        this.updateHiddenInput();
    },

    // Actualizar campo oculto
    updateHiddenInput() {
        const input = document.getElementById('permissions-input');
        if (input) {
            const ids = this.state.assigned.map(p => p.id);
            input.value = JSON.stringify(ids);
        }
    },

    // Actualizar estado de botones
    updateButtonStates() {
        const btnRight = document.getElementById('btn-move-right');
        const btnLeft = document.getElementById('btn-move-left');

        if (btnRight) {
            btnRight.disabled = this.state.selectedIds.available.size === 0;
        }
        if (btnLeft) {
            btnLeft.disabled = this.state.selectedIds.assigned.size === 0;
        }
    },

    // Métodos públicos para actualizar estado desde templates
    updateAvailable(permissions) {
        this.state.available = permissions;
        this.renderList('available');
    },

    updateAssigned(permissions) {
        this.state.assigned = permissions;
        this.renderList('assigned');
        this.updateHiddenInput();
    },

    reset() {
        this.state.search.available = '';
        this.state.search.assigned = '';
        this.state.selectedIds.available.clear();
        this.state.selectedIds.assigned.clear();
        this.renderLists();
        this.updateButtonStates();
    }
};

// Registrar el módulo
if (window.ModuleManager) {
    window.ModuleManager.register('permissionManager', window.PermissionManager);
}