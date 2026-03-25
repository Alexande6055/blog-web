// Sistema de Módulos JavaScript - Gestor Central
window.ModuleManager = {
    modules: new Map(),
    
    // Registrar un módulo
    register(name, module) {
        this.modules.set(name, module);
        console.log(`Módulo ${name} registrado`);
    },
    
    // Inicializar un módulo específico
    initialize(name, data = {}) {
        const module = this.modules.get(name);
        if (module && typeof module.init === 'function') {
            module.init(data);
            console.log(`Módulo ${name} inicializado`);
        } else {
            console.warn(`Módulo ${name} no encontrado o no tiene método init`);
        }
    },
    
    // Inicializar todos los módulos registrados
    initializeAll() {
        this.modules.forEach((module, name) => {
            if (typeof module.init === 'function') {
                module.init();
            }
        });
    },
    
    // Obtener un módulo
    get(name) {
        return this.modules.get(name);
    },
    
    // Verificar si un módulo existe
    has(name) {
        return this.modules.has(name);
    }
};

// Estado global compartido entre módulos
window.AppState = {
    // Estado global de la aplicación
    user: null,
    permissions: [],
    
    // Métodos para actualizar estado
    setUser(userData) {
        this.user = userData;
    },
    
    setPermissions(perms) {
        this.permissions = perms;
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.ModuleManager.initializeAll();
});