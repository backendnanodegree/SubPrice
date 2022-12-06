var Price_Element = document.getElementById("id_price");
Price_Element.setAttribute('value', Number(Price_Element.value).toLocaleString());

function priceToString(price) {
    return price.toLocaleString();
}

$("#id_category_type").change(function () {
    const category_val = $("#id_category_type option:selected").val()  // select box에서 option을 선택하면, 선택된 jquery객체에서 value를 얻습니다.
    $.ajax({
        type: "GET",
        url: "/subscriptions/category_ajax",  // 요청을 보낼 목적 URL, ../app/ajax (path의 name parameter로 찾습니다.)
        // url: "{% url 'category_ajax' %}",  // 요청을 보낼 목적 URL, ../app/ajax (path의 name parameter로 찾습니다.)
        data:{
                "category_val": category_val
                    }, // view로 넘어가는 데이터, category_val 이름으로 넘어갑니다.
        success: function (response) {
                    $("#id_service_type").find("option").remove();  // $("#id_service_type option").remove(); 와 동일합니다. $ -> Jquey식별자
                    let service_val = document.getElementById("id_service_type");
                    let default_service_val_option = document.createElement("option")
                    default_service_val_option.text = "-- 선택 --"
                    default_service_val_option.value = 1
                    service_val.appendChild(default_service_val_option);
                    for (let i = 0; i < response.length; i++){
                        let service_val_option = document.createElement("option");  // tag_name = option으로 Element를 생성합니다.
                        service_val_option.value = response[i][0]; // HTMLOptionElement의 value
                        service_val_option.text = response[i][1];  // HTMLOptionElement의 text 화면에 보인다.
                        service_val.appendChild(service_val_option);
                        // TODO: HTMLOptionElement 상속관계, Node란, HTML DOM API에 대해서...
                    }

        }
    });
})

$("#id_service_type").change(function () {
    const service_val = $("#id_service_type option:selected").val()
    $.ajax({
        type: "GET",
        url: "/subscriptions/service_ajax",
        data:{
                "service_val": service_val
                    },
        success: function (response) {
                    $("#id_plan_type").find("option").remove();
                    let plan_val = document.getElementById("id_plan_type");
                    let default_plan_val_option = document.createElement("option")
                    default_plan_val_option.text = "-- 선택 --"
                    default_plan_val_option.value = 1
                    plan_val.appendChild(default_plan_val_option);
                    for (let i = 0; i < response.length; i++){
                        let plan_val_option = document.createElement("option");
                        plan_val_option.value = response[i][0];
                        plan_val_option.text = response[i][1];
                        plan_val.appendChild(plan_val_option);
                    }

        }
    });
})

$("#id_plan_type").change(function () {
    const plan_val = $("#id_plan_type option:selected").val()
    $.ajax({
        type: "GET",
        url: "/subscriptions/plan_ajax",
        data:{
                "plan_val": plan_val
                    },
        success: function (response) {
                    var response1 = priceToString(response);
                    document.getElementById("id_price").setAttribute('value', response1);
        }
    });
})

$("#id_method_type").change(function () {
    const method_val = $("#id_method_type option:selected").val()
    $.ajax({
        type: "GET",
        url: "/subscriptions/type_ajax",
        data:{
                "method_val": method_val
                    },
        success: function (response) {
                    $("#id_company_type").find("option").remove();
                    let company_val = document.getElementById("id_company_type");
                    let default_company_val_option = document.createElement("option")
                    default_company_val_option.text = "-- 선택 --"
                    default_company_val_option.value = 1
                    company_val.appendChild(default_company_val_option);
                    for (let i = 0; i < response.length; i++){
                        let company_val_option = document.createElement("option");
                        company_val_option.value = response[i][0];
                        company_val_option.text = response[i][1];
                        company_val.appendChild(company_val_option);
                    }

        }
    });
})