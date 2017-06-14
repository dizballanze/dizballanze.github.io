Title: Практикум Zend Framework. Часть первая: Аутентификация и Acl
Date: 2011-06-10 17:09
Author: Admin
Category: Другое
Tags: acl, auth, i18n, layout, registry, route, zend framework
Lang: ru

![Zend Framework][]

В последнее время я все сильнее и сильнее убеждаюсь в универсальности
Zend Framework, как платформы для создания web-приложений. Сегодня я
расскажу о процессе создания каркаса сайта на Zend Framework, который
предоставит необходимую основу для реализации сайтов средней сложности:

-   **Часть первая**

    -   [**Аутентификация**][] - вход пользователей в систему
    -   [**ACL**][] - распределение прав доступа

-   **Часть вторая**

    -   [**Маршрутизация**][] - настройка url для различных компонентов
        системы
    -   [**Registry**][] - быстрый доступ к системным константам

-   **Часть третья**

    -   [**Acl**][] - расширенный пример

Аутентификация
--------------

Аутентификация - неотъемлемая часть практически любого сайта. Как вам
известно для этих целей в Zend Framework используется специальный
компонент Zend\_Auth. Данный компонент позволяет производить процесс
входа в систему путем проверки совпадения пары логин-пароль. Обычно
точкой входа является специальный action аутентификации, а также
возможно экшн регистрации (или подтверждения регистрации). Рассмотрим
простой пример аутентификации:

    :::php
    <? php
    // ...
    public function authAction(){
        $form = new Application_Form_Enter();
        if ($form->isValid($this->getRequest()->getPost())){
            $bootstrap = $this->getInvokeArg('bootstrap');
            $auth = Zend_Auth::getInstance();
            $adapter = $bootstrap->getPluginResource('db')->getDbAdapter();
            $authAdapter = new Zend_Auth_Adapter_DbTable($adapter, 'user', 'login', 'password', 'MD5(?)');
            $authAdapter->setIdentity($form->login->getValue());
            $authAdapter->setCredential($form->password->getValue());
            $result = $auth->authenticate($authAdapter);
            // Если валидация прошла успешно сохраняем в storage инфу о пользователе
            if ($result->isValid()){
                $storage = $auth->getStorage();
                $storage_data = $authAdapter->getResultRowObject(null, array('activate', 'password', 'enabled'));
                $user_model = new Application_Model_DbTable_User();
                $language_model = new Application_Model_DbTable_Language();
                $storage_data->status = 'user';
                $storage->write($storage_data);
            }
        }
    }

Это типичный код аутентификации, который вы можете использовать. Для
полноценной работы вам понадобится соответствующая форма, которая
пересылает логин и пароль на данный action.

После успешной аутентификации пользовательские данные сохраняются в
хранилище (storage) Zend\_Auth. Далее, когда вам потребуется узнать
какую-нибудь информацию о текущем пользователе, вы можете обратится к
Zend\_Auth (он доступен везде, т.к. является реализацией Singleton)
следующим образом:

    :::php
    <?php
    // ...
    $auth = Zend_Auth::getInstance();
    // Если пользователь аутентифицирован
    if ($auth->hasIdentity()){
        // Считываем данные о пользователе
        $user_data = $auth->getStorage()->read();
    }

Также важным действием, которое нужно выполнить, является начальная
инициализация Zend\_Auth при первом заходе пользователя на сайт. Для
этого добавим в bootstrap следующий метод:

    :::php
    <?php
    // ...
    public function _initAuth(){
        $auth = Zend_Auth::getInstance();
        $data = $auth->getStorage()->read();
        if (!isset($data->status)){
            $storage_data = new stdClass();
            $storage_data->status = 'guest';
            $auth->getStorage()->write($storage_data);
        }
    }

Acl
---

В большинстве web-приложений есть несколько статусов доступа, каждый из
которых имеет определённые привилегии. Для большинства сайтов привилегии
и их распределение являются относительно постоянными, поэтому мы
реализуем Acl в виде правил записанных непосредственно в коде программы.
Если же вы разрабатываете систему, которая имеет часто меняющуюся
структуру статусов и прав (например CMS), то вам необходимо строить
более гибкую реализацию Acl, права в которой будут хранится, например, в
базе данных.

Основными задачами, которые должна выполнять система контроля доступа,
является задание привилегий и собственно контроль за доступом. Для
реализации этих задач нам потребуется два компонента:

-   Acl - списки прав доступа
-   Плагин выполняющий проверку корректности доступа текущего
    пользователя к запрашиваемому ресурсу

Рассмотрим самый простой случай, когда ресурсами являются части сайта,
т.е. в терминах MVC - действия. Каждый пользователь наследует права от
некого абстрактного статуса (гость, пользователь, администратор),
привилегии каждого статуса описываются в Acl. Для реализации Acl
расширим Zend\_Acl:

    :::php
    <?php
    // ...
    class Acl extends Zend_Acl {
        public function  __construct() {
            //Добавляем роли
            $this->addRole('guest');
            $this->addRole('user', 'guest');
            $this->addRole('admin', 'user');

            //Добавляем ресурсы
            // РЕСУРСЫ ГОСТЯ !
            $this->add(new Zend_Acl_Resource('guest_allow'));
            $this->add(new Zend_Acl_Resource('index/index'),'guest_allow');
            //...

            // РЕСУРСЫ ПОЛЬЗОВАТЕЛЯ !
            $this->add(new Zend_Acl_Resource('user_allow'));
            $this->add(new Zend_Acl_Resource('user/index'), 'user_allow');
            // ...

            // РЕСУРСЫ АДМИНА !
            $this->add(new Zend_Acl_Resource('admin_allow'));
            $this->add(new Zend_Acl_Resource('admin/index'), 'admin_allow');
            //...        

            //Выставляем права, по-умолчанию всё запрещено
            $this->deny(null, null, null);
            $this->allow('guest', 'guest_allow', 'show');
            $this->allow('user', 'user_allow', 'show');
            $this->allow('admin','admin_allow', 'show');
        }

        public function can($privilege='show'){
            //Инициируем ресурс
            $request = Zend_Controller_Front::getInstance()->getRequest();
            $resource = $request->getControllerName() . '/' . $request->getActionName();
            //Если ресурс не найден закрываем доступ
            if (!$this->has($resource))
                return true;
            //Инициируем роль
            $storage_data = Zend_Auth::getInstance()->getStorage()->read();
            $role = array_key_exists('status', $storage_data)?$storage_data->status : 'guest';
            return $this->isAllowed($role, $resource, $privilege);
        }
    }

Разместите этот код в файле `application/classes/Acl.php`.

Описываем списки прав в стандартной для ZF форме. Также здесь создается
метод, который проверяет права доступа текущего пользователя к текущему
действию. В качестве идентификаторов ресурсов используется формат
controller/action. Если вы проектируете систему таким образом что у вас
права действий внутри контроллера не меняются, то вы можете использовать
вместо идентификаторов ресурсов только имена контроллеров (не забудьте
изменить метод `can`).

Для большей гибкость мы добавляем понятие "привилегия", которая позволит
контролировать определенные действия внутри экшена. Привилегия для
просмотра имеет название "show".

Теперь когда у нас есть список прав доступа и мы умеем определять имеет
ли пользователь доступ к текущему действию, нужно внедрить проверку в
цикл обработки запросов Zend Framework. Для этого лучше всего подходит
создание front controller plugin. Плагины позволяют выполнять заданные
действия на различных этапах процесса диспатчинга:

    :::php
    <?php
    // ...
    class CheckAccess extends Zend_Controller_Plugin_Abstract {
        /**
         * Метод preDispatch выполняет проверку прав доступа на
         * данный controller/action в случае ошибки вызывает метод
         * generateAccessError
         * 
         * @param Zend_Controller_Request_Abstract $request
         */
        public function  preDispatch(Zend_Controller_Request_Abstract $request) {
            $acl = Zend_Controller_Front::getInstance()->getParam('bootstrap')->getResource('Acl');
            if (!$acl->can()){
                $this->generateAccessError();
            }
        }

        /**
         * Метод генерации сообщения о ошибке прав доступа.
         * Выполняет перенаправление на контроллер error и выводит в нём
         * сообщение о ошибке передаваемое в метод.
         * 
         * @param string $msg
         */
        public function generateAccessError($msg='Доступ запрещён!'){
            $request = $this->getRequest();
            $request->setControllerName ('error');
            $request->setActionName('error');
            $request->setParam('message', $msg);
        }
    }

Разместите этот код в файле `application/plugins/CheckAccess.php`.

Этот плагин будет выполнять проверку доступа пользователя при каждом,
запросе поступающем на сайт. Для проверки доступа используется класс
Acl, рассмотренный выше. В случае ошибки запрос будет целенаправлен на
error/error. Для того, чтобы корректно выводилось сообщение об ошибке,
вам нужно добавить соответствующий код в ErrorController.php.

Теперь нужно подключить плагин и создать ресурс Acl в bootstrap:

    :::php
    <?php
    // ...
    public function _initAcl(){
        Zend_Loader::loadClass('Acl');
        Zend_Loader::loadClass('CheckAccess');
        Zend_Controller_Front::getInstance()->registerPlugin(new CheckAccess());
        return new Acl();
    } 

Для того чтобы Zend\_Loader "знал" где искать наши файлы добавим в
application.ini:

    :::ini
    includePaths.plugins = APPLICATION_PATH "/plugins"includePaths.classes = APPLICATION_PATH "/classes"

  [Zend Framework]: /media/2011/06/ZendFramework-logo_small.png
    "Zend Framework"
  [**Аутентификация**]: #auth
  [**ACL**]: #acl
  [**Маршрутизация**]: /PHP/praktikum-zend-framework-chast-vtoraia-route-i-registry/#route
  [**Registry**]: /PHP/praktikum-zend-framework-chast-vtoraia-route-i-registry/#registry
  [**Acl**]: /PHP/praktikum-zend-framework-chast-tretiazend_acl/
