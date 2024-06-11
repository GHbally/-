#include "python.h" 

static PyObject*
spam_strlen(PyObject* self, PyObject* args)
{
    const char* str = NULL;
    int len;

    if (!PyArg_ParseTuple(args, "s", &str)) // �Ű����� ���� �м��ϰ� ���������� �Ҵ� ��ŵ�ϴ�.
        return NULL;

    len = strlen(str);

    return Py_BuildValue("i", len);
}

static PyObject*
spam_division(PyObject* self, PyObject* args)
{
    int quotient = 0;
    int dividend, divisor = 0;

    if (!PyArg_ParseTuple(args, "ii", &dividend, &divisor)) //�������� ���� �Ҵ�
        return NULL;

    if (divisor) {
        quotient = dividend / divisor;
    }
    else {  // ������ 0�� �� ���� ó���� �մϴ�.
        // ���� ó���� �� ���� �ݵ�� NULL�� ���� ���ݴϴ�. PyErr_SetString�Լ��� �׻� NULL�� �����մϴ�.
        //PyExc_ZeroDivisionError�� 0���� �������� �� �� ���� �����Դϴ�.
        PyErr_SetString(PyExc_ZeroDivisionError, "divisor must not be zero");
        return  NULL;
    }

    return Py_BuildValue("i", quotient);
}

static PyObject*
spam_date(PyObject* self, PyObject* args)
{
    const char* str = NULL;
    char year[5];
    char month[3];
    char day[3];

    if (!PyArg_ParseTuple(args, "s", &str)) // �Ű����� ���� �м��ϰ� ���������� �Ҵ� ��ŵ�ϴ�.
        return NULL;

    // ���� ����
    strncpy(year, str, 4);
    year[4] = '\0'; // ���ڿ� ���� ���� �߰�

    // �� ����
    strncpy(month, str + 4, 2);
    month[2] = '\0'; // ���ڿ� ���� ���� �߰�

    // �� ����
    strncpy(day, str + 6, 2);
    day[2] = '\0'; // ���ڿ� ���� ���� �߰�

    return Py_BuildValue("sss", year, month, day);
}


static PyMethodDef SpamMethods[] = {
    {"strlen", spam_strlen, METH_VARARGS,
    "count a string length."},
    {"date", spam_date, METH_VARARGS,
    "division function \n return quotient, quotient is dividend / divisor"},
    {NULL, NULL, 0, NULL},    //�迭�� ���� ��Ÿ����.
    

};


static struct PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",            // ��� �̸�
    "It is test module.", // ��� ������ ���� �κ�, ����� __doc__�� ����˴ϴ�.
    -1,SpamMethods
};

PyMODINIT_FUNC
PyInit_spam(void)
{
    return PyModule_Create(&spammodule);
}
